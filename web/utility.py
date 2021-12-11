import bcrypt

def userExist(db_user,username):
    """Summary or Description of the Function

    Parameters:
    db_user (object): collection of users in the database
    username (str): username of the user

    Returns:
    boolean: True if user exists, False if not

   """

    if db_user.find({"Username":username}).count() == 0:
        return False
    return True

def verify_pw(db_user,username, password):
    """Summary or Description of the Function
    
    Parameters:
    db_user (object): collection of users in the database
    username (str): username of the user
    password (str): password of the user

    Returns:
    boolean: True if password is correct, False if not
    """

    if not userExist(username):
        return False
    
    hashed_pw = db_user.find({
        "Username":username
    })[0]["Password"]

    if bcrypt.hashpw(db_user,password.encode("utf8"),hashed_pw) == hashed_pw:
        return True
    else:
        return False

def generateReturnDictionary(status,msg):
    '''Generate a dictionary of status codes and messages'''
    
    return_json = {
        "status":status,
        "msg":msg
    }
    return return_json

def verifyCredentials(db_user,username, password):
    ''' Verifies the credentials of the user and returns a dictionary of status codes and messages'''

    if not userExist(username):
        return generateReturnDictionary(301,"Invalid username"), True
    
    correct_pw = verify_pw(db_user,username,password)

    if not correct_pw:
        return generateReturnDictionary(302, "Invalid password"), True
    
    return None, False