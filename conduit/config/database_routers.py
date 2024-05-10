class ShardRouter:
    def db_for_read(self, model, **hints):
        """Read articles from the appropriate shard"""

        if model == "articles.Article":
            article_id = hints.get("instance").id
            return "shard1" if article_id % 2 == 0 else "shard2"

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if a model in the same db is involved"""
        db_obj1 = self.db_for_read(type(obj1))
        db_obj2 = self.db_for_read(type(obj2))
        if db_obj1 and db_obj2:
            if db_obj1 == db_obj2:
                return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Allow all models to be migrated to all databases."""
        return True
