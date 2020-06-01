


class Tags(object):

    @staticmethod
    def from_json(tags_json):
        result = []
        for tag_json in tags_json:
            tag = Tag(key=tag_json['Key'], value=tag_json['Value'])

        return result