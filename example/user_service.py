class UserService:
    def __init__(self, database):
        self.database = database

    def create_user(self, name='Some name'):
        """Inserts a user into the database
        :param name: the name of the user
        :return: the ID and the name of the user
        """
        return self.database.insert(name)

    def get_user(self, id):
        """Retrieve the user from the database
        :param id: the ID of the user to retrieve
        :return: the ID and the name
        """
        return self.database.get(id)

    def batch_get_users(self, ids):
        """Retrieves all the users for the provided IDs
        :param ids: the IDs of the users to retrieve
        :return: a list of tuples (id, name)
        """
        return [self.database.get(id) for id in ids]