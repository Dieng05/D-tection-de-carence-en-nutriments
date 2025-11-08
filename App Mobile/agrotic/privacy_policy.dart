// privacy_policy.dart
import 'package:flutter/material.dart';

class PrivacyPolicyPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Politique de Confidentialité"),
        backgroundColor: Colors.green[700],
      ),
      body: Center(
        child: Text("Voici notre politique de confidentialité."),
      ),
    );
  }
}
