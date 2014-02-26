import subprocess

# Same as multiprocessing, but thread only.
# We don't need to spawn new processes for this.
import multiprocessing.dummy

import random
import time
import hashlib
import os


def sha256(path):
    """Return the sha256 digest of the file located at the specified path."""
    h = hashlib.sha256()
    with open(path) as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)

    return h.hexdigest()


class Config(object):
    """Manage the plowshare wrapper configuration.

    Given the path to the configuration file, this
    class handles all configuration parsing and exposes
    it as a python object.

    Currently, this file is composed of only a list
    of plowshare modules to use.

    """
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.host_list = f.read().split()

    def hosts(self):
        """Return the list of available host names."""
        return self.host_list


class Plowshare(object):
    """Upload files using the plowshare tool.

    """
    def __init__(self, config_filename):
        self.cfg = Config(config_filename)

    def random_hosts(self, number_of_hosts):
        """Retrieves a random subset of available hosts.

        The number of hosts provided must not be larger
        than the number of available of hosts, otherwise
        it will throw a ValueError exception.
        """
        return random.sample(self.cfg.hosts(), number_of_hosts)

    def upload(self, filename, number_of_hosts):
        """Uploads the given file to the specified number of hosts."""
        results = self.multiupload(filename, self.random_hosts(number_of_hosts))

        return {
            "version":  "0.1",
            "datetime": str(int(time.time())),
            "filesize": str(os.path.getsize(filename)),
            "filehash": sha256(filename),
            "uploads":  results
        }

    def multiupload(self, filename, hosts):
        """Uploads filename to multiple hosts simultaneously."""
        def f(host):
            return self.upload_to_host(filename, host)

        return multiprocessing.dummy.Pool(len(hosts)).map(f, hosts)

    def upload_to_host(self, filename, hostname):
        """Uploads a file to the given host.

        This method relies on 'plowup' being installed on the system.
        If it succeeds, this method returns a dictionary with the host name,
        and the final URL. Otherwise, it returns a dictionary with the
        host name and an error flag.

        """
        try:
            output = subprocess.check_output(
                ["plowup", hostname, filename],
                stderr=open("/dev/null", "w"))

            output = self.parse_output(hostname, output)
            return { "host_name": hostname, "url": output }

        except subprocess.CalledProcessError:
            return { "host_name": hostname, "error": True }

    def parse_output(self, hostname, output):
        """Parse plowup's output. For now, we just return the last line."""
        return output.split()[-1]
