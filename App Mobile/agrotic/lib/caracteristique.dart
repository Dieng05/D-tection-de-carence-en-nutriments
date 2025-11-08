import 'package:flutter/material.dart';

class CaracteristiquePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Caractéristiques des Plantes"),
        backgroundColor: Colors.green[700], // Couleur de l'app bar
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              "Caractéristiques importantes des plantes",
              style: TextStyle(fontSize: 18),
            ),
            SizedBox(height: 20),
            Text(
              "1. Type de sol\n"
                  "2. Besoins en eau\n"
                  "3. Exposition au soleil\n"
                  "4. Nutriments nécessaires\n",
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // Action pour afficher plus de détails sur les caractéristiques
              },
              child: Text("Voir plus de détails"),
            ),
          ],
        ),
      ),
    );
  }
}
