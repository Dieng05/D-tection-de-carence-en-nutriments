import 'package:flutter/material.dart';
import 'my_drawer_header.dart'; // Assurez-vous que cette page est définie
import 'identification.dart'; // Assurez-vous que cette page est définie
import 'diagnostic_nutriment.dart'; // Assurez-vous que cette page est définie
import 'diagnostic_total.dart'; // Assurez-vous que cette page est définie
import 'caracteristique.dart'; // Assurez-vous que cette page est définie
import 'index.dart'; // Assurez-vous que cette page est définie
import 'package:agrotic/identification_page.dart'; // Remplacez par le chemin correct


void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: HomePage(), // Affiche HomePage au démarrage
    );
  }
}

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  var currentPage = DrawerSections.home; // Défaut à identification

  @override
  Widget build(BuildContext context) {
    var container;

    // Définit le container selon la page sélectionnée
    if (currentPage == DrawerSections.home) {
      container = IndexPage(); // Assurez-vous que cette page est définie
    } else if (currentPage == DrawerSections.identification) {
      container = DiagnosticAndIdentificationPage(); // Assurez-vous que cette page est définie
    } else if (currentPage == DrawerSections.Diagnostic_Nutriment) {
      container = DiagnosticNutrimentPage(); // Assurez-vous que cette page est définie
    } else if (currentPage == DrawerSections.Diagnostic_Total) {
      container = DiagnosticTotalPage(); // Assurez-vous que cette page est définie
    } else if (currentPage == DrawerSections.caracteristique) {
      container = CaracteristiquePage(); // Assurez-vous que cette page est définie
    } else {
      container = Container(); // Défaut si aucune correspondance
    }

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.green[700],
        title: Text("Agrotic"),
      ),
      body: container,
      drawer: Drawer(
        child: SingleChildScrollView(
          child: Column(
            children: [
              MyHeaderDrawer(), // Assurez-vous que cette page est définie
              MyDrawerList(),
            ],
          ),
        ),
      ),
    );
  }

  Widget MyDrawerList() {
    return Container(
      padding: EdgeInsets.only(top: 15),
      child: Column(
        children: [
          menuItem(1, "Acceuil", Icons.dashboard_outlined,
              currentPage == DrawerSections.home),
          menuItem(2, "Identification", Icons.dashboard_outlined,
              currentPage == DrawerSections.identification),
          menuItem(3, "Diagnostic Nutriment", Icons.people_alt_outlined,
              currentPage == DrawerSections.Diagnostic_Nutriment),
          menuItem(4, "Diagnostic Total", Icons.event,
              currentPage == DrawerSections.Diagnostic_Total),
          menuItem(5, "Caractéristiques", Icons.notes,
              currentPage == DrawerSections.caracteristique),
        ],
      ),
    );
  }

  Widget menuItem(int id, String title, IconData icon, bool selected) {
    return Material(
      color: selected ? Colors.grey[300] : Colors.transparent,
      child: InkWell(
        onTap: () {
          Navigator.pop(context);
          setState(() {
            switch (id) {
              case 1:
                currentPage = DrawerSections.home;
                break;
              case 2:
                currentPage = DrawerSections.identification;
                break;
              case 3:
                currentPage = DrawerSections.Diagnostic_Nutriment;
                break;
              case 4:
                currentPage = DrawerSections.Diagnostic_Total;
                break;
              case 5:
                currentPage = DrawerSections.caracteristique;
                break;
            }
          });
        },
        child: Padding(
          padding: EdgeInsets.all(15.0),
          child: Row(
            children: [
              Expanded(
                child: Icon(
                  icon,
                  size: 20,
                  color: Colors.black,
                ),
              ),
              Expanded(
                flex: 3,
                child: Text(
                  title,
                  style: TextStyle(
                    color: Colors.black,
                    fontSize: 16,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Renommer l'enum 'index' en 'home' pour éviter les conflits avec 'enum' de Dart
enum DrawerSections {
  home, // Remplacez 'index' par 'home'
  identification,
  Diagnostic_Nutriment,
  Diagnostic_Total,
  caracteristique,
}
