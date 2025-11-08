import random

synthetic_first_names = {
    'A': ['Alice','Aaron','Ava','Adam','Amelia','Anthony','Abigail','Andrew','Aurora','Alex','Angela','Asher','Anya','Arthur','Autumn','Aiden','Alina','Axel','Alexa','August'],
    'B': ['Bob','Bella','Brandon','Brooke','Benjamin','Bianca','Bryce','Brianna','Blake','Bailey','Brielle','Bryan','Brenda','Beckett','Bryn','Bobby','Brittany','Branson','Bria','Barrett'],
    'C': ['Charlie','Cleo','Caleb','Clara','Christopher','Chloe','Cameron','Camille','Cole','Caitlyn','Connor','Cassandra','Christian','Carla','Cody','Courtney','Colton','Chelsea','Carmen','Clark'],
    'D': ['David','Diana','Daniel','Delilah','Derek','Dakota','Dominic','Daisy','Dylan','Daphne','Damon','Demi','Desmond','Danielle','Diego','Dorothy','Dexter','Dahlia','Donovan','Delaney'],
    'E': ['Eve','Ethan','Ella','Edward','Elijah','Emily','Emmett','Elena','Eric','Esther','Eleanor','Evan','Elsa','Ezekiel','Emilia','Elise','Everett','Edwin','Esme','Elton'],
    'F': ['Fiona','Fred','Faith','Felix','Francis','Farrah','Finn','Flora','Fabian','Felicity','Frank','Freya','Forest','Frances','Finnley','Faye','Fletcher','Fern','Flynn','Farren'],
    'G': ['Grace','George','Gabriel','Gemma','Gideon','Gwen','Gavin','Gloria','Gage','Gianna','Grant','Greta','Giselle','Grayson','Gabriella','Garrett','Griffin','Georgia','Glenn','Guillermo'],
    'H': ['Hannah','Harry','Hazel','Henry','Hope','Hudson','Holly','Hector','Hailey','Hunter','Harmony','Harrison','Heidi','Holden','Helena','Hugo','Harper','Haven','Hale','Hayden'],
    'I': ['Ivy','Ian','Isla','Isaac','Isabel','Imogen','Ivan','Iris','Israel','Indigo','Ida','Ira','Isabella','Ignatius','India','Irving','Ione','Ismael','Ina','Icarus'],
    'J': ['Jack','Jill','James','Julia','Joseph','Jasmine','Jordan','Joy','Jonathan','Jocelyn','Jared','Jade','Justin','Joanna','Joel','Janet','Jeremy','Juniper','Jeremiah','Jean'],
    'K': ['Kate','Kyle','Katherine','Kevin','Kayla','Kai','Kimberly','Kaden','Kara','Kingston','Kenneth','Kylie','Kristen','Kieran','Kiara','Kaleb','Kiwi','Kourtney','Kendrick','Kendall'],
    'L': ['Liam','Luna','Lucas','Lily','Logan','Leah','Leon','Lincoln','Lucia','Levi','Lucy','Landon','Layla','Lorenzo','Liliana','Luke','Lola','Leonardo','Larissa'],
    'M': ['Mia','Max','Matthew','Madeline','Mason','Morgan','Micah','Molly','Miles','Maya','Mitchell','Margaret','Marcus','Melanie','Malcolm','Madison','Marvin','Mariana','Michelle','Maxwell'],
    'N': ['Nora','Nathan','Noah','Naomi','Nicholas','Natalie','Neal','Nina','Nolan','Norah','Nigel','Nova','Norman','Niamh','Nash','Natasha','Nelson','Nico','Nadine','Nyah'],
    'O': ['Olivia','Oscar','Owen','Ophelia','Orion','Octavia','Oliver','Odette','Orlando','Omar','Odyssey','Opal','Otis','Oakley','Odell','Ocean','Olin','Odilia','Ozzy','Onyx'],
    'P': ['Paul','Paula','Peter','Penelope','Patrick','Phoebe','Philip','Piper','Preston','Priscilla','Percy','Paxton','Patricia','Porter','Payton','Paloma','Pierce','Phoenix','Perry','Paige'],
    'Q': ['Quinn','Quincy','Queenie','Quentin','Quade','Quella','Quiana','Quinlan','Quest','Quintin','Quorra','Quinby','Quillon','Quinlan','Quin','Questa','Quintella','Quinette','Quinby','Quillon'],
    'R': ['Ruth','Ryan','Robert','Rebecca','Richard','Rachel','Riley','Rose','Ronald','Ruby','Ronan','Raven','Raymond','Regina','Rocco','Rhea','Roman','Rosalie','Ryder','Reese'],
    'S': ['Sophia','Sam','Samuel','Scarlett','Sebastian','Sienna','Simon','Savannah','Sawyer','Stella','Spencer','Sadie','Silas','Sabrina','Skylar','Shane','Selena','Sterling','Sage','Sydney'],
    'T': ['Tina','Tom','Thomas','Tabitha','Tyler','Theresa','Tristan','Tara','Trevor','Talia','Tobias','Tatiana','Tanner','Tess','Troy','Thalia','Travis','Tiana','Trent','Tobiah'],
    'U': ['Uma','Ulysses','Uriel','Unity','Ulrich','Ursula','Usher','Umaiza','Upton','Ulani','Urban','Udele','Ulma','Ugo','Ulanda','Umar','Ubel','Uriah','Unity','Uri'],
    'V': ['Vera','Victor','Vincent','Vanessa','Valerie','Vance','Vivian','Viola','Violet','Vaughn','Valentina','Virgil','Veda','Vincenzo','Vesper','Virginia','Vittorio','Venus','Vivienne','Valentino'],
    'W': ['Wendy','Will','William','Winona','Walter','Willa','Wyatt','Whitney','Weston','Wren','Wayne','Willow','Wesley','Winter','Wallace','Winslow','Waverly','Waldo','Wynn','Watson'],
    'X': ['Xena','Xander','Xiomara','Xavier','Xyla','Xavion','Xanthe','Xayden','Xeno','Xaria','Ximena','Xzavier','Xavia','Xylon','Xariah','Xerxes','Xanthea','Xenon','Xavia','Xyler'],
    'Y': ['Yara','Yusuf','Yvonne','Yosef','Yasmine','Yvette','Yoel','Yolanda','Yahir','Yadira','Yannis','Yulia','Yarden','Yolande','Yale','Yamir','Yelena','Yuri','Yosefina','Yannis'],
    'Z': ['Zoe','Zach','Zara','Zane','Zion','Zoey','Zander','Zelda','Zayden','Zaria','Zavier','Zella','Zayla','Zephyr','Zionna','Zinnia','Zeke','Zionel','Zelia','Zariah']
}

synthetic_last_names = {
    'A': ['Anderson','Adams','Armstrong','Allen','Albright','Avery','Atkins','Alston','Aiken','Archer','Ashford','Allison','August','Aldridge','Acosta','Appleton','Archeron','Ashby','Ames','Axelson'],
    'B': ['Brown','Baker','Brooks','Bryant','Bell','Benson','Black','Blair','Bradley','Bates','Baldwin','Barrett','Booth','Bowman','Becker','Burgess','Benton','Buckley','Briggs','Browning'],
    'C': ['Clark','Carter','Cole','Collins','Cruz','Chavez','Campbell','Cunningham','Cook','Connor','Caldwell','Craig','Chambers','Carroll','Chester','Casey','Church','Cochran','Clayton','Conway'],
    'D': ['Davis','Diaz','Duncan','Dunn','Douglas','Dorsey','Davidson','Drake','Dalton','Dean','Donovan','Dennis','Dillon','Dawson','Delaney','Desmond','Dudley','Davenport','Donahue','Dahl'],
    'E': ['Evans','Ellis','Edwards','Elliott','Emerson','Erickson','Eastman','Eaton','Elliot','Espinoza','English','Ennis','Elder','Ekstrom','Eberhart','Everett','Egan','Eaton','Elwood','Eldridge'],
    'F': ['Foster','Fox','Franklin','Fleming','Friedman','Farrell','Flynn','Freeman','Faulkner','Ford','Fletcher','Frost','Franks','Foley','Fulton','Ferris','Fitzgerald','Fields','Forbes','Finley'],
    'G': ['Green','Gray','Gonzalez','Garcia','Gibson','Griffin','Gardner','Graham','Gallagher','Grant','Gilbert','Greene','Goodman','Glover','George','Gill','Gates','Glenn','Garrison','Grover'],
    'H': ['Hill','Harris','Hernandez','Howard','Hughes','Hamilton','Henderson','Hammond','Harper','Holt','Hale','Hudson','Hanson','Holmes','Hart','Hobbs','Holt','Hawkins','Hodges','Harrell'],
    'I': ['Ingram','Iverson','Irwin','Irvine','Isley','Ivers','Ingle','Inman','Isaacs','Ibarra','Iversen','Ivins','Iglesias','Illingworth','Inouye','Isett','Irvine','Isom','Isham','Ingalls'],
    'J': ['Johnson','James','Jackson','Jordan','Jennings','Jefferson','Joyce','Jenkins','Jarvis','Jimenez','Juarez','Justice','Jacobs','Jacoby','Johnston','Judd','Joplin','Janis','Jarman','Jurado'],
    'K': ['King','Keller','Kim','Kennedy','Klein','Knight','Kerr','Krause','Keller','Kline','Keith','Kaufman','Keaton','Kendrick','Kane','Kirby','Knox','Kirk','Keller','Kidd'],
    'L': ['Lewis','Long','Lee','Lopez','Lawson','Lynn','Lane','Lancaster','Logan','Lowell','Lamb','Levy','Larsen','Leonard','Lucero','Luna','Lloyd','Lester','Lang','Linden'],
    'M': ['Martin','Moore','Miller','Mitchell','Morgan','Marshall','Morris','Murray','Maxwell','McCarthy','McDonald','Montgomery','Morrison','Maddox','Maynard','McKenzie','Munoz','Madden','Marsh','Mahoney'],
    'N': ['Nelson','Nash','Nguyen','Nichols','Newton','Norton','Nixon','Noble','Neal','Nieves','North','Norwood','Nashville','Norquist','Niven','Noland','Neuman','Nye','Norcross','Norrington'],
    'O': ['Owens','Olsen','Ortiz','Oliver','O’Neal','O’Connor','Odom','Osborne','Oakley','Orr','Ortega','Osgood','Oswald','Overton','Oakes','O’Donnell','Orton','Ogle','Orrick','O’Brien'],
    'P': ['Parker','Price','Phillips','Powell','Peterson','Palmer','Patel','Pierce','Page','Porter','Phelps','Pritchard','Preston','Parsons','Patrick','Paxton','Pennington','Pollard','Patterson','Prince'],
    'Q': ['Quincy','Queen','Quinn','Quigley','Quintana','Quintero','Quimby','Quackenbush','Quest','Quade','Quinlan','Quillen','Quarry','Quintin','Questa','Quade','Quirin','Quella','Quenby','Quell'],
    'R': ['Roberts','Reed','Richardson','Ramirez','Ross','Rogers','Rivera','Russell','Rowe','Riley','Ramos','Reilly','Roy','Rosen','Rutherford','Ray','Rodriguez','Ruben','Roth','Ritchie'],
    'S': ['Smith','Scott','Stewart','Sullivan','Sanders','Simmons','Shaw','Stone','Santiago','Spencer','Shields','Schultz','Snyder','Stephens','Saunders','Shepherd','Salazar','Sharp','Summers','Sawyer'],
    'T': ['Taylor','Turner','Thomas','Torres','Thompson','Tucker','Tran','Todd','Tate','Tyler','Thornton','Tanner','Tillman','Trent','Tobias','Tobin','Teague','Temple','Tremblay','Tracy'],
    'U': ['Underwood','Urban','Upton','Usher','Ulrich','Upchurch','Ulman','Udall','Uribe','Utley','Umbach','Ulmer','Ullman','Uhler','Ulloa','Urbina','Ureña','Udell','Usry','Urbach'],
    'V': ['Vaughn','Valdez','Vega','Vance','Vincent','Valentino','Vazquez','Velasquez','Vinson','Varela','Vickers','Van','Vance','Vann','Vander','Vidal','Villanueva','Vermillion','Vickers','Vo'],
    'W': ['White','Watson','Williams','Wilson','Ward','Wright','Wood','West','Wells','Walker','Winters','Wallace','Walsh','Weston','Wheeler','Westbrook','Whitman','Wilkins','Worthington','Warren'],
    'X': ['Xander','Xiomara','Xenon','Xander','Xyla','Xenakis','Xenos','Xyler','Ximenes','Xiang','Xerxes','Xyla','Xaviera','Xion','Xylia','Xavi','Xenakis','Xandra','Xyra','Xayden'],
    'Y': ['Young','York','Yates','Yu','Yeager','Yoder','Yancey','Yamaguchi','Ybarra','Yoshida','Yamamoto','Yeh','Yilmaz','Yost','Yong','Yarborough','Yule','Yardley','Yule','Yancey'],
    'Z': ['Zimmerman','Zane','Ziegler','Zapata','Zuniga','Zhou','Zeller','Zaragoza','Ziegler','Zamora','Zalewski','Zephyr','Zambrano','Zamudio','Zanetti','Zavala','Zapata','Zander','Zito','Zola']
}

def redact_names(people):
    anonymized_people = []
    for person in people:
        first_initial = person['first_name'][0].upper()
        last_initial = person['last_name'][0].upper()

        new_first = random.choice(synthetic_first_names.get(first_initial, ['AnonF']))
        new_last = random.choice(synthetic_last_names.get(last_initial, ['AnonL']))
        
        anonymized_people.append({'first_name': new_first, 'last_name': new_last})
    return anonymized_people

def anonymize_age(age, max_noise=3):
    """
    Anonymizes an age by adding random noise while keeping it in a similar range.
    :param age: Original age
    :param max_noise: Maximum random deviation (default: 3 years)
    :return: Anonymized age
    """
    noise = (random.random() * 2 * max_noise) - max_noise
    anonymized_age = round(age + noise)
    return max(0, anonymized_age)

if __name__ == '__main__':
    # Example usage
    people_data = [
        {'first_name': 'Bhanu', 'last_name': 'Pingali'},
        {'first_name': 'Alice', 'last_name': 'Johnson'},
        {'first_name': 'Zara', 'last_name': 'Xavier'}
    ]
    print("Redacted Names:", redact_names(people_data))
    print("Anonymized Age (25):", anonymize_age(25))
    print("Anonymized Age (70, 5):", anonymize_age(70, 5))
