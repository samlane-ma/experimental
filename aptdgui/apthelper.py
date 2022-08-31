import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from aptdaemon import client, enums
from aptdaemon.gtk3widgets import AptProgressDialog
import glob


class AptHelper:

    def __init__(self):
        self.set_packages()

        # Set a function to be run on failure or completion (i.e. update GUI)
        self.run_success = None
        self.run_failure = None

        # Setting modal and a transient_for window mitigates issues caused
        # when you don't want the app to be used until apt-daemon completes
        self.window = None
        self.modal = False


    def set_packages(self, install=[], remove=[], purge=[]):
        self.install_list = install
        self.purge_list = remove
        self.remove_list = purge


    def _on_error(self, error):
        # Didn't seem to make sense to add an error dialog here. Most likely,
        # the reason for this to run will be because password prompt is cancelled.
        # We need this though to avoid a crash if cancelled.
        # _on_finished will still be run regardless, with enums.EXIT_FAILED.
        pass


    def _on_failure(self, error):
        error_dialog = Gtk.MessageDialog(type=Gtk.MessageType.ERROR,
                                      buttons=Gtk.ButtonsType.CLOSE,
                                      message_format=error._message)
        error_dialog.run()
        error_dialog.hide()


    def _on_finished(self, dialog):
        self.set_packages()
        if dialog._transaction.exit == enums.EXIT_SUCCESS:
            # What to do when apt is done succesfully
            if self.run_success:
                self.run_success()
        elif dialog._transaction.exit == enums.EXIT_FAILED:
            # What to do when apt is fails
            if self.run_failure:
                self.run_failure()


    def _on_transaction(self, trans):
        trans.set_remove_obsoleted_depends(remove_obsoleted_depends=True)
        apt_dialog = AptProgressDialog(trans)
        if self.modal and self.window:
            apt_dialog.set_modal(True)
            apt_dialog.set_transient_for(self.window)
        apt_dialog.run(error_handler=self._on_error, show_error=False)
        apt_dialog.connect("finished", self._on_finished)


    def run_apt(self, run_success=None, run_failure=None):
        # On completion, run_success function will be run if successful
        # or run_failure if there was an issue.
        self.run_success = run_success
        self.run_failure = run_failure

        install =  self.install_list
        remove = []
        purge = []

        # check if requested remove/purge packages are installed
        for pkg in (self.remove_list):
            if pkg != glob.glob('/var/lib/dpkg/info/%s.list' % pkg):
                remove.append(pkg)
        for pkg in (self.purge_list):
            if pkg != glob.glob('/var/lib/dpkg/info/%s.list' % pkg):
                purge.append(pkg)

        if len(install+purge+remove) == 0:
            # Nothing to do
            if self.run_success:
                self.run_success()
            return

        apt_client = client.AptClient()
        apt_client.update_cache()
        apt_client.commit_packages(install=install, reinstall=[], remove=remove,
                                   purge=purge, upgrade=[], downgrade=[],
                                   error_handler=self._on_failure,
                                   reply_handler=self._on_transaction)