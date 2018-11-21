import os

import git


class HistoryManager:
    """ Class for managing version history of a notebook
    """

    def __init__(self, path: str, git_dir: str = '.history', remote: str = None):
        self.git_dir = os.path.join(path, git_dir)
        self.repo = git.Repo.init(self.git_dir, bare=True)
        self.repo.working_dir = self.git_dir
        self.remote = remote
        # TODO if remote is provided, ensure that credentials are provided as well

    def make_checkpoint(self, message: str = None) -> bool:
        """ Creates a checkpoint in history
        :param message: The message to go with the checkpoint. If no message is provided, the default message is just a
        timestamp
        :return: True if the checkpoint is successfully created
        """
