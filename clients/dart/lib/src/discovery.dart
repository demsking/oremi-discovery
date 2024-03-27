import 'package:oremi_core/oremi_core.dart';
import 'package:oremi_discovery_client/src/models.dart';

typedef OnServiceDataCallback = void Function(ServiceEvent);
typedef OkResultCallback = void Function(OkResult);

class DiscoveryClient extends WebsocketJsonRpcClient {
  DiscoveryClient({
    required String uri,
    required String userAgent,
  }) : super(uri: uri, userAgent: userAgent);

  Future<void> publish(ServiceEvent event, {OkResultCallback? onDone}) async {
    print('> $event');
    await sendRequest(
      'register',
      params: event.toJson(),
      onResponse: onDone != null ? (data) => onDone(OkResult.fromJson(data)) : null,
    );
  }

  Future<void> watch(String name, OnServiceDataCallback onServiceData) async {
    await sendRequest(
      'subscribe',
      params: {'name': name},
      onResponse: (data) => onServiceData(ServiceEvent.fromJson(data)),
    );
  }

  Future<void> unwatch(String name, {OkResultCallback? onDone}) async {
    await sendRequest(
      'unsubscribe',
      params: {'name': name},
      onResponse: onDone != null ? (data) => onDone(OkResult.fromJson(data)) : null,
    );
  }
}
