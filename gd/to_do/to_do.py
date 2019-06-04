stuff = """
/*
	CHK values (download): LevelID, Inc, RS, AccountID, UDID, UUID
	CHK values (upload): Seed
	generate it using the function ```GenerateLevelUploadSeed()```
*/
LEVEL_KEY
/*
	CHK values: Username, Comment, LevelID, Percentage, Comment Type (0 = Level, 1 = User)
*/ HOW WOULD I EVEN GET PERCENTAGE?
COMMENT_KEY
/*
	CHK values: Random[5], Random Number
*/
CHALLENGES_KEY #this needs to be rewritten tbh
/*
	CHK values: Random[5], Random Number
*/
REWARDS_KEY
/*
	CHK values (like): Special, ItemID, Like, Type, RS, AccountID, UDID, UUID
	CHK values (rate): LevelID, Stars, RS, AccountID, UDID, UUID
*/
LIKERATE_KEY
/*
	CHK values: AccountID, UserCoins, Demons, Stars, Coins, IconType, Icon, Diamonds, AccIcon, AccShip, AccBall, AccBird, AccDart, AccRobot, AccGlow, AccSpider, AccExplosion
*/
USERSCORE_KEY
/*
	CHK values: AccountID, LevelID, Percentage, Seconds, Jumps, Attempts, Seed, Bests Differences, UNKNOWN (always 1), UserCoins, DailyID, Seed7 ("s7" from packet)
	Seconds = seconds taken to reach the best
	Jumps = jumps taken to reach the best
	Bests Differences = differences between bests, ex: 0% - 65% - 100% -> (65 - 0), (100 - 65) -> 65,35
	Generate Seed using the function "GenerateLevelLeaderboardSeed()"
*/
const auto LEVELSCORE_KEY = "39673";
"""