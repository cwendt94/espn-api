from espn_api.football import League as fb_league
from espn_api.basketball import League as bb_league
from spontit import SpontitResource
import time
import sys

starttime = time.time()
resource = SpontitResource('jwill24', 'QC1I1NE14I2XHBW55Q04OEHCTDR5RELMHAFZUKT4OCBHJ25VZ2WV0OZUDJL6LGKVVHI2YV3E84P3CCVJEMCNMC4ZOSC2QO38UISK')
goat_league = fb_league(league_id=90359061, year=2020, espn_s2='AEBV%2BW%2F%2F1DGOy1iiBpocpFpegxEcV4ZhLWoeTzr%2BNQ8pCwar1AqPMqmI8u%2FA%2BIv0ii7WFXRM1e%2FTU3B6YNbn1sgisIdAOIMzpW2PFGFHJpQfBor%2BL5xdqw78xQZhbbxMZDonn4xo0xW%2BbqLwOEv0dc%2BHjWz8NNBfST6f0z9%2BT13LXh77Sln5cs\
dofCEPm2n2LoXe2cUOXLB6rW4rB4N4czYFWgH70TDFMUIT1dDZ%2FMrCrwXE%2BJ9ej5NaAoz9XoJC6B3SPbQaksTpq4KeaVQz6eeH', swid='{9404E72D-02B1-41C9-84E7-2D02B191C9FC}' )
kt_league = bb_league(league_id=79672, year=2020, espn_s2='AECESfzTnGtRTZ6HqNd54yWHn8olsPY%2BMApaNrV3Ra8pYXQZp%2BpG7Ni7G6xZduEKLC5RvtHaMhGh7KtVNFLnVZwNWFIyI3gdXVIBlmQ5z4P5yl%2BuSKhsADdm%2BTkliQarWoDyQ7ctXt%2BXUZoeJw534Xmv6lzz5dDux6MLsUhkdpvSGQs0WDkuBKVRrV8wqOw7yzFLc1eEM2beEEKrqPXwniNmtYJc5fsapC8CVdj0m0hL7U6xGtLSebvq6kQbjkZwVfoWAaiqU2tU17ljpzO9Hcs2', swid='{9404E72D-02B1-41C9-84E7-2D02B191C9FC}')

#-------------------------

def sendMessage(activity,league):

    a = activity.split(',')

    if league == 'goat':
        if 'ADDED' in a[1]: n_a, n_d = 2, 4
        elif 'ADDED' in a[3]: n_a, n_d = 4, 2
        else: resource.push('TRADE ALERT!')

        team = a[0][a[0].find('Team(')+5:a[0].find(')')]
        add = a[n_a][:a[n_a].find(')')]
        drop = a[n_d][:a[n_d].find(')')]
        activity_string = team + ' added ' + add + ' and dropped ' + drop
        
    elif league == 'kt':
        team = a[0][a[0].find('Team(')+5:a[0].find(')')]
        activity_string = team + ' made a transaction!'

    resource.push(activity_string)
    #print(activity_string) # FIXME: for testing


#-------------------------


tmp_goat = goat_league.recent_activity()[0]
tmp_kt = kt_league.recent_activity()[0].date
#tmp_goat = 'initialize' # FIXME: for testing
#tmp_kt = 'initialize' # FIXME: for testing

while True:
    activity_goat = goat_league.recent_activity()
    activity_kt = kt_league.recent_activity()

    # Check GOAT League
    if str(tmp_goat) != str(activity_goat[0]):
        print('Alert!')
        sendMessage(str(activity_goat[0]),'goat')
        tmp_goat = activity_goat[0]

    # Check KT League
    if str(tmp_kt) != str(activity_kt[0].date):
        print('Alert!')
        sendMessage(str(activity_kt[0]),'kt')
        tmp_kt = activity_kt[0].date

    sys.stdout.write("\rTime running: {} Seconds".format(round(time.time()-starttime,2)))
    sys.stdout.flush()
    time.sleep(30.0 - ((time.time() - starttime) % 30.0)) # check every 30 seconds                                                                                                                                                                                                      
    
