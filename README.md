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
                         [--ignore-ids IGNORE_IDS]
                         [--critical {LOW,MEDIUM,HIGH,CRITICAL}]
                         [--warning {LOW,MEDIUM,HIGH,CRITICAL}]

Check output of testssl.sh

optional arguments:
  -h, --help            show this help message and exit
  --uri URI             host|host:port|URL|URL:port.Port 443 is default, URL
                        can only contain HTTPS protocol
  --testssl TESTSSL     Path to the testssl.sh script
  --ignore-ids IGNORE_IDS
                        Comma separated list of test IDs to ignore
  --critical {LOW,MEDIUM,HIGH,CRITICAL}
                        Findings of this severity level trigger a CRITICAL
  --warning {LOW,MEDIUM,HIGH,CRITICAL}
                        Findings of this severity level trigger a WARNING
```
# Examples

Checking a URI with default severity levels:

```
vagrant@buster:~$ ./nagios-testssl.py --testssl /opt/testssl/testssl.sh \
  --uri https://www.geant.org
WARNING: 2 issues found for https://www.geant.org with severity HIGH or higher.
HIGH: secure_client_renego (VULNERABLE, DoS threat)
HIGH: BREACH (potentially VULNERABLE, uses gzip HTTP compression  - only supplied '/' tested)
```

The same URI, but ignoring two tests:
```
vagrant@buster:~$ ./nagios-testssl.py --testssl /opt/testssl/testssl.sh \
  --uri https://www.geant.org --ignore-ids BREACH,secure_client_renego
OK: No issues found for https://www.geant.org with severity HIGH or higher.
```

Another URI with default severity levels:

```
vagrant@buster:~$ ./nagios-testssl.py --testssl /opt/testssl/testssl.sh \
  --uri https://login.geant.org
OK: No issues found for https://login.geant.org with severity HIGH or higher.
```


The same URI, but we lowered the severity that will trigger alarms. Instead of
the default HIGH, we now get notified when a MEDIUM issue is detected:

```
vagrant@buster:~$ ./nagios-testssl.py --testssl /opt/testssl/testssl.sh \
  --uri https://login.geant.org --critical HIGH --warning MEDIUM
OK: No issues found for https://login.geant.org with severity MEDIUM or higher.
```
