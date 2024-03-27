class Service {
  final String name;
  final String protocol;
  final String host;
  final int port;
  final Map<String, dynamic>? data;

  Service({
    required this.name,
    required this.protocol,
    required this.host,
    required this.port,
    this.data,
  });

  String get uri => '$protocol://$host:$port';

  @override
  String toString() => 'Service(name: $name, uri: $uri, data: $data)';

  Map<String, dynamic> toJson() => {
    'name': name,
    'protocol': protocol,
    'host': host,
    'port': port,
    'data': data,
  };

  static Service fromJson(Map<String, dynamic> json) => Service(
    name: json['name'],
    protocol: json['protocol'],
    host: json['host'],
    port: json['port'],
    data: json['data'],
  );
}

class ServiceEvent {
  final String status;
  final Service service;

  ServiceEvent({
    required this.status,
    required this.service,
  });

  @override
  String toString() => 'Event(status: $status, service: $service)';

  Map<String, dynamic> toJson() => {
    'status': status,
    'service': service.toJson(),
  };

  static ServiceEvent fromJson(Map<String, dynamic> json) => ServiceEvent(
    status: json['status'],
    service: Service.fromJson(json['service']),
  );
}

class ServiceNameParams {
  final String name;

  ServiceNameParams({required this.name});
}

class Request {
  final int id;
  final String method;
  final Map<String, dynamic> params;
  final String jsonrpc;

  Request({
    required this.id,
    required this.method,
    required this.params,
    this.jsonrpc = '2.0',
  });
}

class OkResult {
  final bool ok;

  OkResult({required this.ok});

  Map<String, dynamic> toJson() => {
    'ok': ok,
  };

  static OkResult fromJson(Map<String, dynamic> json) => OkResult(
    ok: json['ok'],
  );

  @override
  String toString() => 'Result(ok: $ok)';
}

class Response {
  final int id;
  final dynamic result;
  final String jsonrpc;

  Response({
    required this.id,
    required this.result,
    this.jsonrpc = '2.0',
  });
}
