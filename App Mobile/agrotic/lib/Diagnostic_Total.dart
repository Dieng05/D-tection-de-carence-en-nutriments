import 'package:flutter/material.dart';
import 'dart:io'; // Pour la gestion des fichiers d'image
import 'package:image_picker/image_picker.dart'; // Pour utiliser la caméra et la galerie
import 'package:http/http.dart' as http; // Pour faire des requêtes HTTP
import 'package:path/path.dart'; // Pour la manipulation de chemins de fichiers
import 'package:mime/mime.dart'; // Pour obtenir le type MIME
import 'package:http_parser/http_parser.dart'; // Import nécessaire pour MediaType
import 'dart:convert'; // Pour le décodage JSON

class DiagnosticTotalPage extends StatefulWidget {
  @override
  _DiagnosticTotalPageState createState() => _DiagnosticTotalPageState();
}

class _DiagnosticTotalPageState extends State<DiagnosticTotalPage> {
  File? _selectedImage; // Stocke l'image sélectionnée
  final ImagePicker _picker = ImagePicker();
  Map<String, dynamic> _result = {}; // Variable pour stocker le résultat de l'API

  // Méthode pour prendre une image avec la caméra
  Future<void> _pickImageFromCamera() async {
    final pickedFile = await _picker.pickImage(source: ImageSource.camera);
    if (pickedFile != null) {
      setState(() {
        _selectedImage = File(pickedFile.path);
      });
    }
  }

  // Méthode pour sélectionner une image depuis la galerie
  Future<void> _pickImageFromGallery() async {
    final pickedFile = await _picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _selectedImage = File(pickedFile.path);
      });
    }
  }

  // Méthode pour envoyer l'image et obtenir le diagnostic total
  Future<void> _uploadImage(File imageFile) async {
    final uri = Uri.parse("http://192.168.43.231:8000/All"); // Remplacez par votre endpoint

    var request = http.MultipartRequest('POST', uri);

    var mimeType = lookupMimeType(imageFile.path);
    var file = await http.MultipartFile.fromPath(
      'file',
      imageFile.path,
      contentType: MediaType.parse(mimeType ?? 'image/jpeg'),
    );

    request.files.add(file);

    try {
      var response = await request.send();

      if (response.statusCode == 200) {
        var responseData = await http.Response.fromStream(response);
        setState(() {
          _result = json.decode(responseData.body);
        });
      } else {
        var responseData = await http.Response.fromStream(response);
        setState(() {
          _result = {"error": "Erreur lors de l'envoi de l'image : ${response.reasonPhrase}, Détails : ${responseData.body}."};
        });
      }
    } catch (e) {
      setState(() {
        _result = {"error": "Erreur lors de l'envoi de l'image : $e."};
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Diagnostic Total"),
        backgroundColor: Colors.green[700],
      ),
      body: SingleChildScrollView(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (_selectedImage == null) ...[
                Text(
                  "Choisir une image pour le diagnostic total",
                  style: TextStyle(fontSize: 18),
                ),
                SizedBox(height: 20),
                ElevatedButton.icon(
                  onPressed: _pickImageFromCamera,
                  icon: Icon(Icons.camera_alt, color: Colors.white),
                  label: Text("Caméra"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,
                  ),
                ),
                SizedBox(height: 20),
                ElevatedButton.icon(
                  onPressed: _pickImageFromGallery,
                  icon: Icon(Icons.photo, color: Colors.white),
                  label: Text("Galerie"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                  ),
                ),
              ] else ...[
                Image.file(
                  _selectedImage!,
                  height: 300,
                  width: 300,
                ),
                SizedBox(height: 20),
                if (_result.isEmpty || _result.containsKey("error"))
                  ElevatedButton.icon(
                    onPressed: () => _uploadImage(_selectedImage!),
                    icon: Icon(Icons.analytics, color: Colors.white),
                    label: Text("Démarrer le diagnostic total"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                    ),
                  ),
                SizedBox(height: 20),
                if (_result.isNotEmpty && !_result.containsKey("error"))
                  _buildResultTable(),
              ]
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildResultTable() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: Column(
        children: [
          Text(
            "Résultats du diagnostic total",
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 10),
          Table(
            border: TableBorder.all(),
            children: [
              TableRow(
                children: [
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Text("Nutriments", style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Text("Niveau", style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Text("Pourcentage", style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
              ..._result.entries.map((entry) {
                String nutrient = entry.key;
                var details = entry.value;
                return TableRow(
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Text(nutrient),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Text(details['level'].toString()),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Text(details['percentage'].toStringAsFixed(2)),
                    ),
                  ],
                );
              }).toList(),
            ],
          ),
        ],
      ),
    );
  }
}
