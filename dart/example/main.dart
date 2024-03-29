import 'dart:async';
import 'dart:io';
import 'package:args/args.dart';
import 'package:oremi_discovery/src/discovery.dart';
import 'package:oremi_discovery/src/models.dart';

Future<void> main(List<String> args) async {
  final completer = Completer<void>();
  final parser = ArgParser()
    ..addOption(
      'host',
      abbr: 'h',
      defaultsTo: 'localhost',
      help: 'Host address to connect to (default: localhost).',
    )
    ..addOption(
      'port',
      abbr: 'p',
      defaultsTo: '5105',
      help: 'Port number to connect to (default: 5105).',
    )
    ..addOption(
      'cert-file',
      help: 'Path to the certificate file for secure connection.',
    );

  final argResults = parser.parse(args);
  final service = Service(
    name: 'mqtt',
    protocol: 'mqtt',
    host: 'test.mosquitto.org',
    port: 1883,
    data: {'version': '1.0.0'},
  );

  final host = '${argResults['host']}:${argResults['port']}';
  SecurityContext? sslContext;

  if (argResults['cert-file'] != null) {
    print('Using certificate file "${argResults['cert-file']}"');
    sslContext = SecurityContext.defaultContext;
    sslContext.setTrustedCertificates(argResults['cert-file']);
  }

  final client = DiscoveryClient(
    uri: sslContext != null ? 'wss://$host' : 'ws://$host',
    userAgent: 'Discovery Client/1.0.0',
  );

  await client.connect();
  final event = ServiceEvent(status: 'ONLINE', service: service);
  await client.publish(event, onDone: (result) => print('Subscribing result: $result'));
  await Future.delayed(Duration(seconds: 1));
  await client.watch('mqtt', (event) => print('Watching service event: $event'));
  await Future.delayed(Duration(seconds: 1));
  await client.unwatch('mqtt', onDone: (result) => print('Unwatching result: $result'));
  await Future.delayed(Duration(seconds: 1));
  await client.disconnect();
  completer.complete();

  // Wait for the connection to complete before exiting
  await completer.future;
}
