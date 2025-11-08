import 'package:flutter/material.dart';

class DiagnosticNutrimentPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Diagnostic des Nutriments"),
        backgroundColor: Colors.green[700], // Couleur de l'app bar
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              "Diagnostic des nutriments de la plante",
              style: TextStyle(fontSize: 18),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // Action pour démarrer le diagnostic
              },
              child: Text("Commencer le diagnostic"),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // Action pour afficher les résultats du diagnostic
              },
              child: Text("Afficher les résultats"),
            ),
          ],
        ),
      ),
    );
  }
}
