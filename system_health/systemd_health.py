from checks import AgentCheck
import shlex
import socket


class SystemdHealthCheck(AgentCheck):
    COMMAND="systemctl --system --no-legend --plain --state=failed"

    def _check_health(self,tags):
        commnad = shlex.split(self.COMMAND)
        msg=""
        hostname = socket.gethostbyaddr(socket.gethostname())[0].split('.')[0]
        try:
            out, err, retcode = get_subprocess_output(commnad, self.log, raise_on_empty_output=True)
            if retcode != 0:
                msg = err
                self.service_check('systemd_health.is_unknown', 3, tags=tags, hostname=hostname, message=msg)
            elif out:
                for failed_unit in out.split('\n'):
                    msg += failed_unit.split(' ')[0]
                self.service_check('systemd_health.is_critical', 2, tags=tags, hostname=hostname, message=msg)
            else:
                msg = "OK"
                self.service_check('systemd_health.is_ok', 0, tags=tags, hostname=hostname, message=msg)
        except Exception as e:
            msg = e
            self.service_check('systemd_health.is_unknown', 3, tags=tags, hostname=hostname, message=msg)
               
    def check(self,instance):
        tags = instance.get('tags', [])
        self._check_health(self,tags)