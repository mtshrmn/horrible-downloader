class DownloadsManager:
    def __init__(self, directory, data):
        self.directory = directory
        self.data = data

    def _filter(self, quality):
        """
        returns the important url needed for the download
        :param quality:
        :return:
        """
        pass

    def download(self):
        """
        in charge of downloading the file
        :return:
        """
        pass

    def on_complete(self):
        """
        hook the download completion to update the user.
        :return:
        """
        pass
