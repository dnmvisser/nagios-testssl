# nagios-testssl

Python wrapper around https://github.com/drwetter/testssl.sh for use as a
Nagios/Icinga plugin.

# Installation and requirements

Obviously you will need a copy of the testssl.sh script. In recent distros this
is available through the OS package manager. This is a very easy way to install
it, but the version will stay the same more or less forever. This means you
will probably end up missing out of recent TLS/crypto issues.
A better approach is cloning the upstream git repository. This way you have the
latest version, which is also easy to update in the future:

```bash
sudo apt-get install git python3-jmespath
git clone https://github.com/drwetter/testssl.sh.git /opt/testssl
```


# Usage

```
usage: nagios-testssl.py [-h] --uri URI --testssl TESTSSL
                         [--critical {OK,INFO,LOW,MEDIUM,HIGH,CRITICAL}]
                         [--warning {OK,INFO,LOW,MEDIUM,HIGH,CRITICAL}]
                         ...

Check output of testssl.sh

positional arguments:
  trailing_args

optional arguments:
  -h, --help            show this help message and exit
  --uri URI             host|host:port|URL|URL:port.Port 443 is default, URL
                        can only contain HTTPS protocol
  --testssl TESTSSL     Path to the testssl.sh script
  --critical {OK,INFO,LOW,MEDIUM,HIGH,CRITICAL}
                        Findings of this severity level trigger a CRITICAL
  --warning {OK,INFO,LOW,MEDIUM,HIGH,CRITICAL}
                        Findings of this severity level trigger a WARNING
```

# Examples

Checking a URI with default severity levels:

```
vagrant@buster:~$ ./nagios-testssl/nagios-testssl.py --testssl /opt/testssl/testssl.sh \
  --uri https://www.geant.org
WARNING: 2 issues found for https://www.geant.org with severity HIGH or higher.
HIGH: secure_client_renego (VULNERABLE, DoS threat)
HIGH: BREACH (potentially VULNERABLE, uses gzip HTTP compression  - only supplied '/' tested)
```


Another URI with default severity levels:

``
vagrant@buster:~$ ./nagios-testssl.py --testssl /opt/testssl/testssl.sh \
  --uri https://login.geant.org
OK: No issues found for https://login.geant.org with severity HIGH or higher.
```


The same URI, but we lowered the severity that will trigger alarms. Instead of
the default HIGH, we now get notified when a MEDIUM issue is detected:

```
vagrant@buster:~$ nagios-testssl/nagios-testssl.py --testssl /opt/testssl/testssl.sh \
  --uri https://login.geant.org --critical HIGH --warning MEDIUM
OK: No issues found for https://login.geant.org with severity MEDIUM or higher.
```


Trigger on _all_ issues. Interesting - but not very useful for monitoring purposes:

```
vagrant@buster:~$ ./nagios-testssl/nagios-testssl.py --testssl /opt/testssl/testssl.sh \
  --uri https://www.google.com --critical OK --warning OK
CRITICAL: 176 issues found for https://www.google.com with severity OK or higher.
HIGH: BREACH (potentially VULNERABLE, uses gzip HTTP compression  - only supplied '/' tested)
MEDIUM: cipherlist_3DES_IDEA (offered)
MEDIUM: BEAST_CBC_TLS1 (ECDHE-ECDSA-AES128-SHA ECDHE-ECDSA-AES256-SHA ECDHE-RSA-AES128-SHA ECDHE-RSA-AES256-SHA AES128-SHA AES256-SHA DES-CBC3-SHA)
LOW: TLS1 (offered (deprecated))
LOW: TLS1_1 (offered (deprecated))
LOW: cipherlist_AVERAGE (offered)
LOW: TLS_session_ticket (valid for 100800 seconds (>daily))
LOW: OCSP_stapling <cert#1> (not offered)
LOW: OCSP_stapling <cert#2> (not offered)
LOW: HSTS (not offered)
LOW: SWEET32 (uses 64 bit block ciphers)
LOW: BEAST (VULNERABLE -- but also supports higher protocols  TLSv1.1 TLSv1.2 (likely mitigated))
LOW: LUCKY13 (potentially vulnerable, uses TLS CBC ciphers)
INFO: pre_128cipher (No 128 cipher limit bug)
INFO: NPN (offered with grpc-exp, h2, http/1.1 (advertised))
INFO: ALPN (http/1.1grpc-exp)
INFO: PFS_ciphers (TLS_AES_256_GCM_SHA384 TLS_CHACHA20_POLY1305_SHA256 ECDHE-RSA-AES256-GCM-SHA384 ECDHE-ECDSA-AES256-GCM-SHA384 ECDHE-RSA-AES256-SHA ECDHE-ECDSA-AES256-SHA ECDHE-ECDSA-CHACHA20-POLY1305 ECDHE-RSA-CHACHA20-POLY1305 TLS_AES_128_GCM_SHA256 ECDHE-RSA-AES128-GCM-SHA256 ECDHE-ECDSA-AES128-GCM-SHA256 ECDHE-RSA-AES128-SHA ECDHE-ECDSA-AES128-SHA)
INFO: cipherorder_TLSv1 (ECDHE-ECDSA-AES128-SHA ECDHE-ECDSA-AES256-SHA ECDHE-RSA-AES128-SHA ECDHE-RSA-AES256-SHA AES128-SHA AES256-SHA DES-CBC3-SHA)
INFO: cipherorder_TLSv1_1 (ECDHE-ECDSA-AES128-SHA ECDHE-ECDSA-AES256-SHA ECDHE-RSA-AES128-SHA ECDHE-RSA-AES256-SHA AES128-SHA AES256-SHA DES-CBC3-SHA)
INFO: cipherorder_TLSv1_2 (ECDHE-ECDSA-CHACHA20-POLY1305 ECDHE-ECDSA-AES128-GCM-SHA256 ECDHE-ECDSA-AES256-GCM-SHA384 ECDHE-ECDSA-AES128-SHA ECDHE-ECDSA-AES256-SHA ECDHE-RSA-CHACHA20-POLY1305 ECDHE-RSA-AES128-GCM-SHA256 ECDHE-RSA-AES256-GCM-SHA384 ECDHE-RSA-AES128-SHA ECDHE-RSA-AES256-SHA AES128-GCM-SHA256 AES256-GCM-SHA384 AES128-SHA AES256-SHA DES-CBC3-SHA)
INFO: TLS_extensions ('renegotiation info/#65281' 'EC point formats/#11' 'session ticket/#35' 'next protocol/#13172' 'key share/#51' 'supported versions/#43' 'extended master secret/#23' 'application layer protocol negotiation/#16')
INFO: SSL_sessionID_support (yes)
INFO: sessionresumption_ticket (supported)
INFO: sessionresumption_ID (supported)
INFO: TLS_timestamp (off by 0 seconds from your localtime)
INFO: cert_numbers (2)
INFO: cert_keySize <cert#1> (RSA 2048 bits)
INFO: cert_keyUsage <cert#1> (Digital Signature, Key Encipherment)
INFO: cert_extKeyUsage <cert#1> (cert_ext_keyusage)
INFO: cert_serialNumber <cert#1> (B832F6C5BE358C020800000000320AA9)
INFO: cert_fingerprintSHA1 <cert#1> (C7696D7A697748D688CD8C226231D294CD468C93)
INFO: cert_fingerprintSHA256 <cert#1> (5A03A29DAE4C2FF11980AE2EB3DD101495206BFE48B70757B299C55A4D774AC5)
INFO: cert <cert#1> (-----BEGIN CERTIFICATE----- MIIFizCCBHOgAwIBAgIRALgy9sW+NYwCCAAAAAAyCqkwDQYJKoZIhvcNAQELBQAw QjELMAkGA1UEBhMCVVMxHjAcBgNVBAoTFUdvb2dsZSBUcnVzdCBTZXJ2aWNlczET MBEGA1UEAxMKR1RTIENBIDFPMTAeFw0yMDAzMDMwOTQ1NTJaFw0yMDA1MjYwOTQ1 NTJaMGgxCzAJBgNVBAYTAlVTMRMwEQYDVQQIEwpDYWxpZm9ybmlhMRYwFAYDVQQH Ew1Nb3VudGFpbiBWaWV3MRMwEQYDVQQKEwpHb29nbGUgTExDMRcwFQYDVQQDEw53 d3cuZ29vZ2xlLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOsG BXpTDutwvQ/iVIg7/Z/r8thSgauiXw/tbT5nCVK/7AlsU2ELv8uhImpNdfteA8hy /7M7NbYtcv0M+deAc6NKwyaLBAblBX+kv2TFn7xozsc6OeAahoH2CSy/XD+RQ2Uw 2TEFC6qqXrFAmmhxq/vJArMtx7hFcz3AugCm+EBTHPw0O8JQ++w2e2cm5sQNU0yo XUFijBpgwd8ao6o5vxQowU3Ll1LqTxVH+05AGP9pYAgBw/V1oLO55uJCyDA49NM9 Tu/JCcRdIYHmkzsmG1lYHVhHFNReTNUJktM+JUPWIuUVKZ4vtRnl+N3cfRRSZA6D pWd8RWj9N5HUYLzFRhUCAwEAAaOCAlQwggJQMA4GA1UdDwEB/wQEAwIFoDATBgNV HSUEDDAKBggrBgEFBQcDATAMBgNVHRMBAf8EAjAAMB0GA1UdDgQWBBRie0J7d0P3 ZRHofG6m15SHZfquLDAfBgNVHSMEGDAWgBSY0fhuEOvPm+xgnxiQG6DrfQn9KzBk BggrBgEFBQcBAQRYMFYwJwYIKwYBBQUHMAGGG2h0dHA6Ly9vY3NwLnBraS5nb29n L2d0czFvMTArBggrBgEFBQcwAoYfaHR0cDovL3BraS5nb29nL2dzcjIvR1RTMU8x LmNydDAZBgNVHREEEjAQgg53d3cuZ29vZ2xlLmNvbTAhBgNVHSAEGjAYMAgGBmeB DAECAjAMBgorBgEEAdZ5AgUDMC8GA1UdHwQoMCYwJKAioCCGHmh0dHA6Ly9jcmwu cGtpLmdvb2cvR1RTMU8xLmNybDCCAQQGCisGAQQB1nkCBAIEgfUEgfIA8AB2ALIe BcyLos2KIE6HZvkruYolIGdr2vpw57JJUy3vi5BeAAABcKAAg3wAAAQDAEcwRQIh AMJ/c8ZbNPsSen29pgnNHYpB3gaqkvGLj8A1OQh426qgAiA8xl9x0O9E5iHnw8eA HAFtNzNksUKgi9eZF1Syoso6fgB2AF6nc/nfVsDntTZIfdBJ4DJ6kZoMhKESEoQY dZaBcUVYAAABcKAAg7UAAAQDAEcwRQIhAJv2i8XAkvaydDFbrLSjH0AxEy/lp+zp 9xcNXL4wiq6cAiAmOQEF8x98iI/g3V29uRam3llGAYJk/hfh+q/EVuGvBTANBgkq hkiG9w0BAQsFAAOCAQEAkLRZ5s4RGALv9+sZCL0F4+1FxZPiNyTWEpZsrJhfb6rM AZQnrFNw4yjV+W+aQSvdZPWvk51ZOfY9OxwW3mhmG59v/XfOvsj/E+1mACHcIqtn HwPWIKZm/nNY8q+7jhj+5XqvPXSrLpo3F+8QX4EBOldLtZBJM9nEyfVBSnZidyxk swIgWkMZ59JEg3xrouKCZvKp4vLaHXKsxK6Hv24CqNI/5efv0vYmrb5w/0Uk+OqB +r0mkiUYHVArDMbQuK/zfiKCOCSZ+hh9yQyqsfPeh5LecT9b9XXTDe2gcESZTrxI d/OiDxO4NtHAqm9/NV9oZD/KghjdEoyUjs8X3vFrYg== -----END CERTIFICATE-----)
INFO: cert_commonName_wo_SNI <cert#1> (www.google.com)
INFO: cert_subjectAltName <cert#1> (www.google.com)
INFO: cert_caIssuers <cert#1> (GTS CA 1O1 (Google Trust Services from US))
INFO: cert_certificatePolicies_EV <cert#1> (no)
INFO: cert_eTLS (not present)
INFO: cert_notBefore <cert#1> (2020-03-03 09:45)
INFO: cert_validityPeriod <cert#1> (No finding)
INFO: certs_countServer <cert#1> (2)
INFO: certs_list_ordering_problem <cert#1> (no)
INFO: cert_crlDistributionPoints <cert#1> (http://crl.pki.goog/GTS1O1.crl)
INFO: cert_ocspURL <cert#1> (http://ocsp.pki.goog/gts1o1)
INFO: cert_mustStapleExtension <cert#1> (--)
INFO: cert_keyUsage <cert#2> (Digital Signature)
INFO: cert_extKeyUsage <cert#2> (cert_ext_keyusage)
INFO: cert_serialNumber <cert#2> (2E06FAFDA61CDF2302000000005C6778)
INFO: cert_fingerprintSHA1 <cert#2> (F9D63C0F77F9CABD8AD9B61640A1627E40F7F7DD)
INFO: cert_fingerprintSHA256 <cert#2> (CC40C11B6F428E4EE9CADD11B1804B607C450CEB593CAFB4B4C2494FADF18E71)
INFO: cert <cert#2> (-----BEGIN CERTIFICATE----- MIIEvzCCA6egAwIBAgIQLgb6/aYc3yMCAAAAAFxneDANBgkqhkiG9w0BAQsFADBC MQswCQYDVQQGEwJVUzEeMBwGA1UEChMVR29vZ2xlIFRydXN0IFNlcnZpY2VzMRMw EQYDVQQDEwpHVFMgQ0EgMU8xMB4XDTIwMDMwMzA5NDU1MloXDTIwMDUyNjA5NDU1 MlowaDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCkNhbGlmb3JuaWExFjAUBgNVBAcT DU1vdW50YWluIFZpZXcxEzARBgNVBAoTCkdvb2dsZSBMTEMxFzAVBgNVBAMTDnd3 dy5nb29nbGUuY29tMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEO4J/9ejqFR5u UfjQq/CNkPVxkUpZWJH5mYpb1J36NTGrYXBcUCyg96oSfewJayu9yb07QoGAizdA wyCBCIhZKqOCAlQwggJQMA4GA1UdDwEB/wQEAwIHgDATBgNVHSUEDDAKBggrBgEF BQcDATAMBgNVHRMBAf8EAjAAMB0GA1UdDgQWBBShMg0FlfLCfwDLxp79g5vN2gKY jjAfBgNVHSMEGDAWgBSY0fhuEOvPm+xgnxiQG6DrfQn9KzBkBggrBgEFBQcBAQRY MFYwJwYIKwYBBQUHMAGGG2h0dHA6Ly9vY3NwLnBraS5nb29nL2d0czFvMTArBggr BgEFBQcwAoYfaHR0cDovL3BraS5nb29nL2dzcjIvR1RTMU8xLmNydDAZBgNVHREE EjAQgg53d3cuZ29vZ2xlLmNvbTAhBgNVHSAEGjAYMAgGBmeBDAECAjAMBgorBgEE AdZ5AgUDMC8GA1UdHwQoMCYwJKAioCCGHmh0dHA6Ly9jcmwucGtpLmdvb2cvR1RT MU8xLmNybDCCAQQGCisGAQQB1nkCBAIEgfUEgfIA8AB1ALIeBcyLos2KIE6HZvkr uYolIGdr2vpw57JJUy3vi5BeAAABcKAAhBgAAAQDAEYwRAIgENKkBGPAFEetGUQO kmhmkJDEciICxOnjs0D4Y7JWkr8CIFPJ7583F4XxDuZPJp2BJxQTKvNwtvXmaLhr v/TrWPdHAHcAXqdz+d9WwOe1Nkh90EngMnqRmgyEoRIShBh1loFxRVgAAAFwoACE RwAABAMASDBGAiEA1t9gDIOT+I7CMpxP1m5lkJjxreXiXj2WnR/J5AdPMoMCIQCG fYlEMlEd2uYVsp/YNUtZZjsLruZFc2sinAcY/d8sGjANBgkqhkiG9w0BAQsFAAOC AQEAKUG67YovyMnfyQd90RHGKf1qIUK6S+vwlTJ5TtAzv7KjhPxdBFO73GQV7VsY mpMnaIbNd+armZxoNt1VxkLZK6eCbuKt2MY9ZMDT0upxFyA+B/lttuGGRI/M30BJ 1u1C0LlUqlHIzG1cokcJuKIdB9/09wGkYui1xmM1R/Ath+vyu8o+6VHhLDnMYsnk ANH3i1lxzhh+dOHvrz99j3IEg6B1FzbC18QhYmhjiyawgiEwjNf3PL08mj08vjkm Z4+DkDSeSz5niB5IJpZ+cECmiNdktC+XZrxboItBaLY8qqNUvNQ39jbJhkbClhds N+lVK8H4v2doBo529XMfa5WfYQ== -----END CERTIFICATE-----)
INFO: cert_commonName_wo_SNI <cert#2> (www.google.com)
INFO: cert_subjectAltName <cert#2> (www.google.com)
INFO: cert_caIssuers <cert#2> (GTS CA 1O1 (Google Trust Services from US))
INFO: cert_certificatePolicies_EV <cert#2> (no)
INFO: cert_eTLS (not present)
INFO: cert_notBefore <cert#2> (2020-03-03 09:45)
INFO: cert_validityPeriod <cert#2> (No finding)
INFO: certs_countServer <cert#2> (2)
INFO: certs_list_ordering_problem <cert#2> (no)
INFO: cert_crlDistributionPoints <cert#2> (http://crl.pki.goog/GTS1O1.crl)
INFO: cert_ocspURL <cert#2> (http://ocsp.pki.goog/gts1o1)
INFO: cert_mustStapleExtension <cert#2> (--)
INFO: HTTP_status_code (200 OK ('/'))
INFO: HTTP_clock_skew (0 seconds from localtime)
INFO: HPKP (No support for HTTP Public Key Pinning)
INFO: banner_server (gws)
INFO: banner_application (No application banner found)
INFO: cookie_count (2 at '/')
INFO: cookie_secure (1/2 at '/' marked as secure)
INFO: cookie_httponly (1/2 at '/' marked as HttpOnly)
INFO: Cache-Control (private, max-age=0)
INFO: banner_reverseproxy (--)
INFO: DROWN_hint (Make sure you don't use this certificate elsewhere with SSLv2 enabled services, see https://censys.io/ipv4?q=5A03A29DAE4C2FF11980AE2EB3DD101495206BFE48B70757B299C55A4D774AC5)
INFO: cipher_x1302 (x1302   TLS_AES_256_GCM_SHA384            ECDH 253   AESGCM      256      TLS_AES_256_GCM_SHA384)
INFO: cipher_x1303 (x1303   TLS_CHACHA20_POLY1305_SHA256      ECDH 253   ChaCha20    256      TLS_CHACHA20_POLY1305_SHA256)
INFO: cipher_xc030 (xc030   ECDHE-RSA-AES256-GCM-SHA384       ECDH 256   AESGCM      256      TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384)
INFO: cipher_xc02c (xc02c   ECDHE-ECDSA-AES256-GCM-SHA384     ECDH 256   AESGCM      256      TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384)
INFO: cipher_xc014 (xc014   ECDHE-RSA-AES256-SHA              ECDH 256   AES         256      TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA)
INFO: cipher_xc00a (xc00a   ECDHE-ECDSA-AES256-SHA            ECDH 256   AES         256      TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA)
INFO: cipher_xcca9 (xcca9   ECDHE-ECDSA-CHACHA20-POLY1305     ECDH 253   ChaCha20    256      TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256)
INFO: cipher_xcca8 (xcca8   ECDHE-RSA-CHACHA20-POLY1305       ECDH 253   ChaCha20    256      TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256)
INFO: cipher_x9d (x9d     AES256-GCM-SHA384                 RSA        AESGCM      256      TLS_RSA_WITH_AES_256_GCM_SHA384)
INFO: cipher_x35 (x35     AES256-SHA                        RSA        AES         256      TLS_RSA_WITH_AES_256_CBC_SHA)
INFO: cipher_x1301 (x1301   TLS_AES_128_GCM_SHA256            ECDH 253   AESGCM      128      TLS_AES_128_GCM_SHA256)
INFO: cipher_xc02f (xc02f   ECDHE-RSA-AES128-GCM-SHA256       ECDH 256   AESGCM      128      TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256)
INFO: cipher_xc02b (xc02b   ECDHE-ECDSA-AES128-GCM-SHA256     ECDH 256   AESGCM      128      TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256)
INFO: cipher_xc013 (xc013   ECDHE-RSA-AES128-SHA              ECDH 256   AES         128      TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA)
INFO: cipher_xc009 (xc009   ECDHE-ECDSA-AES128-SHA            ECDH 256   AES         128      TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA)
INFO: cipher_x9c (x9c     AES128-GCM-SHA256                 RSA        AESGCM      128      TLS_RSA_WITH_AES_128_GCM_SHA256)
INFO: cipher_x2f (x2f     AES128-SHA                        RSA        AES         128      TLS_RSA_WITH_AES_128_CBC_SHA)
INFO: cipher_x0a (x0a     DES-CBC3-SHA                      RSA        3DES        168      TLS_RSA_WITH_3DES_EDE_CBC_SHA)
INFO: clientsimulation-android_442 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-android_500 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-android_60 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-android_70 (TLSv1.2 ECDHE-ECDSA-CHACHA20-POLY1305)
INFO: clientsimulation-android_81 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-android_90 (TLSv1.3 TLS_AES_128_GCM_SHA256)
INFO: clientsimulation-android_X (TLSv1.3 TLS_AES_128_GCM_SHA256)
INFO: clientsimulation-chrome_74_win10 (TLSv1.3 TLS_AES_128_GCM_SHA256)
INFO: clientsimulation-chrome_79_win10 (TLSv1.3 TLS_AES_128_GCM_SHA256)
INFO: clientsimulation-firefox_66_win81 (TLSv1.3 TLS_AES_128_GCM_SHA256)
INFO: clientsimulation-firefox_71_win10 (TLSv1.3 TLS_AES_128_GCM_SHA256)
INFO: clientsimulation-ie_6_xp (No connection)
INFO: clientsimulation-ie_8_win7 (TLSv1.0 ECDHE-ECDSA-AES128-SHA)
INFO: clientsimulation-ie_8_xp (TLSv1.0 DES-CBC3-SHA)
INFO: clientsimulation-ie_11_win7 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-ie_11_win81 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-ie_11_winphone81 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-ie_11_win10 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-edge_15_win10 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-edge_17_win10 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-opera_66_win10 (TLSv1.3 TLS_AES_128_GCM_SHA256)
INFO: clientsimulation-safari_9_ios9 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-safari_9_osx1011 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-safari_10_osx1012 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-safari_121_ios_122 (TLSv1.3 TLS_CHACHA20_POLY1305_SHA256)
INFO: clientsimulation-safari_130_osx_10146 (TLSv1.3 TLS_CHACHA20_POLY1305_SHA256)
INFO: clientsimulation-apple_ats_9_ios9 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-java_6u45 (TLSv1.0 AES128-SHA)
INFO: clientsimulation-java_7u25 (TLSv1.0 ECDHE-ECDSA-AES128-SHA)
INFO: clientsimulation-java_8u161 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-java1102 (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-java1201 (TLSv1.3 TLS_AES_128_GCM_SHA256)
INFO: clientsimulation-openssl_102e (TLSv1.2 ECDHE-ECDSA-AES128-GCM-SHA256)
INFO: clientsimulation-openssl_110l (TLSv1.2 ECDHE-ECDSA-CHACHA20-POLY1305)
INFO: clientsimulation-openssl_111d (TLSv1.3 TLS_AES_256_GCM_SHA384)
INFO: clientsimulation-thunderbird_68_3_1 (TLSv1.3 TLS_AES_128_GCM_SHA256)
OK: SSLv2 (not offered)
OK: SSLv3 (not offered)
OK: TLS1_2 (offered)
OK: TLS1_3 (offered with final)
OK: ALPN_HTTP2 (h2)
OK: cipherlist_NULL (not offered)
OK: cipherlist_aNULL (not offered)
OK: cipherlist_EXPORT (not offered)
OK: cipherlist_LOW (not offered)
OK: cipherlist_STRONG (offered)
OK: PFS (offered)
OK: PFS_ECDHE_curves (prime256v1 X25519)
OK: cipher_order (server -- TLS 1.3 client determined)
OK: protocol_negotiated (Default protocol TLS1.3)
OK: cipher_negotiated (TLS_AES_256_GCM_SHA384, 253 bit ECDH (X25519))
OK: cert_signatureAlgorithm <cert#1> (SHA256 with RSA)
OK: cert_commonName <cert#1> (www.google.com)
OK: cert_trust <cert#1> (Ok via SAN (same w/o SNI))
OK: cert_chain_of_trust <cert#1> (passed.)
OK: cert_expirationStatus <cert#1> (60 >= 60 days)
OK: cert_notAfter <cert#1> (2020-05-26 09:45)
OK: DNS_CAArecord <cert#1> (issue=pki.goog)
OK: certificate_transparency <cert#1> (yes (certificate extension))
OK: cert_signatureAlgorithm <cert#2> (SHA256 with RSA)
OK: cert_keySize <cert#2> (EC 256 bits)
OK: cert_commonName <cert#2> (www.google.com)
OK: cert_trust <cert#2> (Ok via SAN (same w/o SNI))
OK: cert_chain_of_trust <cert#2> (passed.)
OK: cert_expirationStatus <cert#2> (60 >= 60 days)
OK: cert_notAfter <cert#2> (2020-05-26 09:45)
OK: DNS_CAArecord <cert#2> (issue=pki.goog)
OK: certificate_transparency <cert#2> (yes (certificate extension))
OK: X-Frame-Options (SAMEORIGIN)
OK: X-XSS-Protection (0)
OK: heartbleed (not vulnerable, no heartbeat extension)
OK: CCS (not vulnerable)
OK: ticketbleed (not vulnerable)
OK: ROBOT (not vulnerable)
OK: secure_renego (supported)
OK: secure_client_renego (not vulnerable)
OK: CRIME_TLS (not vulnerable)
OK: POODLE_SSL (not vulnerable, no SSLv3)
OK: fallback_SCSV (supported)
OK: FREAK (not vulnerable)
OK: DROWN (not vulnerable on this host and port)
OK: LOGJAM (not vulnerable, no DH EXPORT ciphers,)
OK: LOGJAM-common_primes (no DH key with <= TLS 1.2)
OK: RC4 (not vulnerable)
```
