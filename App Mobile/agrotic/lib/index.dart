import 'package:flutter/material.dart';

class IndexPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        //title: Text('Sanar Agrotic'),
        backgroundColor: Colors.green[700],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: GridView.count(
          crossAxisCount: 2, // Deux colonnes
          mainAxisSpacing: 16.0, // Espacement vertical
          crossAxisSpacing: 16.0, // Espacement horizontal
          children: <Widget>[
            createButton('Identification\nPlantes', Colors.green, () {
              // Naviguer vers la page d'identification
            }),
            createButton('Diagnostic\nTotal', Colors.orange, () {
              // Naviguer vers la page de diagnostic total
            }),
            createButton('Diagnostic\nPar Carence', Colors.pink, () {
              // Naviguer vers la page de diagnostic par carence
            }),
            createButton('Détails\nCaractéristiques', Colors.blue, () {
              // Naviguer vers la page des détails des caractéristiques
            }),
          ],
        ),
      ),
    );
  }

  Widget createButton(String title, Color color, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: color,
          borderRadius: BorderRadius.circular(10),
        ),
        child: Center(
          child: Text(
            title,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }
}
