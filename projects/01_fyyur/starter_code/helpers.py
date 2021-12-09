from datetime import datetime
from models import Show
from sqlalchemy import case
#----------------------------------------------------------------------------#
# Helper Functions.
#----------------------------------------------------------------------------#

def castStart_time(start_time):
    '''
    Method used to cast the start_time multiple time
    '''
    return start_time.strftime("%Y-%m-%dT%H:%M:%S")

def isShowUpcoming(start_time):
    '''
    The main purpose of this method is know if a show is upcoming or not. It casts the start_time that is in the DB
    '''
    if datetime.now() < start_time:
        return True
    else:
        return False

def concat_genres(list_genres):
    '''
    In case that multiples genres are chosed, the same key appears multiple time, to concat them to string this method is needed
    '''
    genre_casted = ', '.join(list_genres)
    return genre_casted

def get_case_upfront():
  '''
  This case method is used several times to cound the number of show that are upfront, this way we can rehuse it
  '''
  return case(
    [
        (Show.start_time>datetime.now(), 1)  
    ],
    else_=0
  ) 