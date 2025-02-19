"""
Database routers for the conduit project.
"""

class ShardRouter:
    """
    A router to control database operations.
    For now, this is a simple implementation that routes all operations to the default database.
    In the future, this can be expanded to support database sharding.
    """
    
    def db_for_read(self, model, **hints):
        """
        Reads go to the default database.
        """
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Writes go to the default database.
        """
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if both objects are in the default database.
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All migrations go to the default database.
        """
        return True 