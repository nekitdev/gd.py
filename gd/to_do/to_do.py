stuff = """
/*
	CHK values: Seed
	(generated with gen_level_lb_seed())
*/
LEVEL

/*
	CHK values: Random[5], Random Number
*/
CHALLENGES

/*
	CHK values: Random[5], Random Number
*/
REWARDS

/*
	CHK values: AccountID, UserCoins, Demons, Stars, Coins, IconType, Icon, Diamonds, AccIcon, AccShip, AccBall, AccBird, AccDart, AccRobot, AccGlow, AccSpider, AccExplosion
*/
USERSCORE
/*
	CHK values: AccountID, LevelID, Percentage, Seconds, Jumps, Attempts, Seed, Bests Differences, UNKNOWN (always 1), UserCoins, DailyID, Seed7 ("s7" from packet)
	Seconds = seconds taken to reach the best
	Jumps = jumps taken to reach the best
	Bests Differences = differences between bests, ex: 0% - 65% - 100% -> (65 - 0), (100 - 65) -> 65,35
	Generate Seed using the function "GenerateLevelLeaderboardSeed()"
*/
LEVELSCORE
"""
