from datetime import datetime

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


    
    