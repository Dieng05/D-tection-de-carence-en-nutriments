// send_feedback.dart
import 'package:flutter/material.dart';

class SendFeedbackPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Envoyer des Retours"),
        backgroundColor: Colors.green[700],
      ),
      body: Center(
        child: Text("Votre retour est important pour nous."),
      ),
    );
  }
}
