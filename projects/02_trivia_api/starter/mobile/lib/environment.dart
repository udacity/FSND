const _baseUrl = "";

enum Environment { DEV_DEVICE, DEV_ANDROID_EMULATOR }

Map<String, dynamic> _config = Map<String, dynamic>();

void setEnvironment(Environment env) {
  switch (env) {
    case Environment.DEV_DEVICE:
      _config = deviceDevConstant;
      break;
    case Environment.DEV_ANDROID_EMULATOR:
      _config = emulatorAndroidDevConstatnt;
      break;
  }
}

dynamic get apiBaseUrl {
  return _config[_baseUrl];
}

Map<String, dynamic> deviceDevConstant = {
  _baseUrl: "http://10.0.0.23:5000/api",
};

Map<String, dynamic> emulatorAndroidDevConstatnt = {
  _baseUrl: "http://10.0.2.2:5000/api",
};
