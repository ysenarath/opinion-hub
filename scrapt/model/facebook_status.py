from scrapt.model.___abc import Status, Comment


class FacebookComment(Comment):
    def __init__(self, comment_id, status_id, parent_id, comment_message, comment_author, comment_published,
                 num_reactions, num_likes, num_loves, num_wows, num_hahas, num_sads, num_angrys, num_special):
        super(FacebookComment, self).__init__()
        self.comment_id = comment_id
        self.status_id = status_id
        self.parent_id = parent_id
        self.comment_message = comment_message
        self.comment_author = comment_author
        self.comment_published = comment_published
        self.num_reactions = num_reactions
        self.num_likes = num_likes
        self.num_loves = num_loves
        self.num_wows = num_wows
        self.num_hahas = num_hahas
        self.num_sads = num_sads
        self.num_angrys = num_angrys
        self.num_special = num_special


class FacebookStatus(Status):
    def __init__(self, status_id, status_message, link_name, status_type, status_link, status_published, num_reactions,
                 num_comments, num_shares, num_likes, num_loves, num_wows, num_hahas, num_sads, num_angrys,
                 num_special, comments):
        super(FacebookStatus, self).__init__()
        self.status_id = status_id
        self.status_message = status_message
        self.link_name = link_name
        self.status_type = status_type
        self.status_link = status_link
        self.status_published = status_published
        self.num_reactions = num_reactions
        self.num_comments = num_comments
        self.num_shares = num_shares
        self.num_likes = num_likes
        self.num_loves = num_loves
        self.num_wows = num_wows
        self.num_hahas = num_hahas
        self.num_sads = num_sads
        self.num_angrys = num_angrys
        self.num_special = num_special
        self.comments = comments
