from datetime import datetime
import dateutil.parser
import babel


class Utils:

    @staticmethod
    def str_to_date(date_string):
        return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def create_search_data(search_id, name, num_of_shows):
        return {
            "id": search_id,
            "name": name,
            "num_upcoming_shows": num_of_shows
        }


