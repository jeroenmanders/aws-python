from infraxys.model.base_object import BaseObject
from .generic.tags import Tags
from .generic.tag import Tag


class AwsBaseObject(BaseObject):

    def __init__(self):
        super().__init__()
        self.session = None
        self.loaded_from_aws = False
        self.tags = None

    def get_name_filter(self, name):
        return {
            'Name':'tag:Name',
            'Values': [ name ]
        }

    def set_tags_json(self, tags_json):
        self.tags = Tags.from_json(tags_json)

    def check_exactly_one_instance(self, json, collection_name, label, fail_if_not_found):
        count = len(json[collection_name])
        if count == 0:
            if fail_if_not_found:
                self.logger.fatal("{} not found".format(label))

            return
        elif count > 1:
            self.logger.fatal("More than one {} found".format(label))

        return json[collection_name][0]