1: # Programing for Data Science
2: 
3: Phenomena and data
4: 
5: Hugo Alatrista-Salas
6: 
7: hugo.alatrista_salas@devinci.fr
8: 
9: *De Vinci Higher Education, La Défense, Paris*
10: # Motivation
11: # Phenomenon: volcanic eruption
12: 
13: # Volcanic Earthquakes
14: 
15: ![img-1.jpeg](img-1.jpeg)
16: # Facts about a volcanic eruption
17: 
18: |  Year | Month | Day | TSU | EQ | Name | Location | Country | Latitude | Longitude | Elevation | Type | Status | Time | VEI | Agent | DEATHS  |
19: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
20: |  DEATHS | DESCRIPTION |  | MISSING |  | MISSING | DESCRIPTION |  | INJURIES |  | DAMAGE | MILLIONS | DOLLARS |  | HOUSES | DESTROYED |   |
21: |  HOUSES | DESTROYED | DESCRIPTION |  | TOTAL | DEATHS | TOTAL | DEATHS | DESCRIPTION | TOTAL | MISSING | DESCRIPTION | TOTAL | INJURIES | TOTAL | INJURIES | DESCRIPTION  |
22: |  |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
23: |  |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
24: |  TOTAL | DAMAGE | MILLIONS | DOLLARS |  | TOTAL | DAMAGE | DESCRIPTION | TOTAL | HOUSES | DESTROYED | TOTAL | HOUSES | DESTROYED | TOTAL | INJURIES | DESCRIPTION  |
25: |  -4360 |  |  |  |  | Macaulay Island | Kermadec Is |  | New Zealand | -30.2 | -178.47 | 238 | Caldera Holocene |  | U | 6 |   |
26: |  -4350 |  |  |  |  | Kikai Ryukyu Is | Japan | 30.78 | 130.28 | 717 | Caldera | Historical | D1 | 7 | P | 3 |   |
27: |  -4050 |  |  | 3 |  | Masaya Nicaragua | Nicaragua |  | 11.984 | -86.161 | 635 | Caldera | Historical | D1 | 6 |  |   |
28: |  -4000 |  |  |  |  | Pago New Britain-SW Pac |  |  | Papua New Guinea |  | -5.58 | 150.52 | 742 | Caldera | Historical | D2 | 6  |
29: |  -3580 | 1 |  |  |  | Taal Luzon-Philippines |  |  | Philippines | 14.002 | 120.993 | 400 | Stratovolcano | Historical |  | D1 | 6  |
30: |  -3550 |  |  |  |  | Pinatubo Luzon-Philippines |  |  | Philippines | 15.13 | 120.35 | 1486 | Stratovolcano | Historical |  | D1 | 6  |
31: |  -2040 |  |  |  |  | Long Island New Guinea-NE of |  |  | Papua New Guinea |  | -5.358 | 147.12 | 1280 | Complex volcano | Historical |  | D1 6  |
32: |  -1900 |  |  |  |  | Black Peak Alaska Peninsula |  |  | United States | 56.53 | -158.8 | 1032 | Stratovolcano | Radiocarbon |  | D7 | 6  |
33: |  -1860 |  |  |  |  | St. Helens US-Washington |  |  | United States | 46.2 | -122.18 | 2549 | Stratovolcano | Historical |  | D1 | 6  |
34: |  -1750 |  |  |  |  | Veniaminof Alaska Peninsula |  |  | United States | 56.17 | -159.38 | 2507 | Stratovolcano | Historical |  | D1 | 6  |
35: |  -1645 |  |  |  |  | Aniakchak Alaska Peninsula |  |  | United States | 56.88 | -158.17 | 1341 | Caldera | Historical |  | D2 | 6  |
36: |  -1610 |  |  | TSU | EQ | Santorini Greece | Greece | 36.404 | 25.396 | 329 | Shield volcano | Historical | D2 | 6 | W |  |   |
37: |  -1550 |  |  | TSU |  | Redoubt Alaska-SW |  |  | United States | 60.48 | -152.75 | 3108 | Stratovolcano | Historical |  | D1 |   |
38: |  -1460 |  |  |  |  | Taupo New Zealand |  |  | New Zealand | -38.82 | 176 | 760 | Caldera | Radiocarbon |  | D6 | 6  |
39: # Modeling of phenomena
40: # Representation of the world
41: 
42: ![img-2.jpeg](img-2.jpeg)
43: 
44: Sabina Leonelli. What distinguishes data from models? European Journal for Philosophy of Science, Springer, Jan 2019.
45: # VOLCANO ANATOMY
46: 
47: A network of a replicate in this room of a planetary mass object, such as Earth, that allows hot lava,
48: soft ash, ash, and gases to escape from a magma chamber before this surface.
49: 
50: ![img-4.jpeg](img-4.jpeg)
51: # Objects, attributes and data (1)
52: 
53: - The world can be represented by a collection of objects and the attributes that describe them
54: - An attribute is a property or characteristic of an object
55: 
56: - E.g., person's eye color or temperature.
57: - Attributes are also known as variables, fields, or characteristics
58: 
59: - Collections of attributes describe an object
60: - Objects may or may not belong to a class
61: 
62: - Certain characteristics of an object may determine the class to which it belong
63: - Classes can range from two (binary) to more (multi-class)
64: 
65: - An instance of an object is known as a record, point, entity, or individual.
66: # Objects, attributes and data (2)
67: 
68: - Data or attribute values are numbers or symbols assigned to an attribute or characteristic of an object
69: - Differences between attributes and data (or attribute values)
70: 
71: - A piece of data can take different values, but they generally respond to only one type. For example, distance can be measured in feet or meters. Feet can be integers and meters can be real numbers
72: - Different attributes can be assigned to the same data domain; for example, the values for the number of children and age are integers. The age domain is an integer value between 0 and 120.
73: - Data domains can differ. For example, ID has no limit, but age has a maximum and minimum value
74: # Nominal and Ordinal Attributes
75: 
76: - Nominal: categories, states, or names of things
77: 
78: - e.g., days of the week = Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday
79: - Other examples are marital status, occupation, ID, eye color, etc.
80: 
81: - Ordinal: values that imply an order (ranking)
82: 
83: - The magnitude between successive values is unknown
84: - e.g., size = small, medium, large
85: - e.g., evaluation of the acceptance of Lay's Chips (scale of 1-10)
86: # Binary attributes
87: 
88: - They are nominal attributes with only two states, e.g., 0 and 1
89: - Symmetric binaries: both values have the same importance, e.g., sex = {male, female}
90: - Asymmetric binaries: not symmetric. e.g., medical tests positive, negative
91: - By convention, we assign a value of 1 to the most important item (e.g., an infected patient or a satisfied customer)
92: # Discrete and Continuous Attributes
93: 
94: - Discrete (categorical) attributes
95: 
96: - Have only finite values, e.g., telephone numbers, letters in a document, professions, etc.
97: - Sometimes represented by an integer value
98: - Note: binary attributes are a particular type of discrete attribute
99: 
100: - Continuous attributes
101: 
102: - Have real numbers as attribute values, e.g., temperature, weight, height, etc.
103: - Are typically represented by floating-point numbers. In practice, values can be represented by a finite number of digits
104: # Exercises
105: 
106: 1. Data scientists at the bank are interested in studying the credit risk of their clients. Give two examples of binary attributes (with their possible values), two discrete attributes and two continuous attributes that can be used in this study
107: 2. A questionnaire is associated with the study of our clients, and the following attributes are taken into account: a) age, b) sex, c) profession, d) height, and e) number of children. Indicate the types of data used for each attribute
108: 3. An employee notes the order in which clients pay their debts. The first one has already paid, the second one, ... Which type of attributes are being used?
109: 4. In the marketing area, a study is being carried out on clients' perceptions of the totems annonces used by a bank. The idea is to analyze facial expressions captured by a camera and determine the polarity in the expressions of the individuals studied. What attribute type will be used and what values can this attribute have?
110: 5. The aim is to study the impact of temperature on the purchasing habits of the bank's clients. The data is collected daily for a year. How would you group the data so that it is binary? For example, I group it by quarter but the attribute is not binary, but nominal
111: # Answers
112: 
113: 1. Binary: sex (male, female), debtor (yes, no), has a card (yes, no), etc.
114:    Discrete: number of children, number of cards, etc.
115:    Continuous: balance in your account, APR of your last loan, etc.
116: 2. There are many ways to answer this question. Discrete a), c) and d), continuous d), binary b)
117: 3. Ordinal
118: 4. Nominal, with positive, neutral and negative values
119: 5. Period={summer season, cold season}
120: # Data modeling
121: # Representation of phenomena with data
122: 
123: Data captures and conveys the same information about the world, regardless of the circumstances of the research and, in particular, the assumptions and backgrounds of the researchers who use it as evidence¹.
124: 
125: ¹Sabina Leonelli. What distinguishes data from models? European Journal for Philosophy of Science, Springer, Jan 2019.
126: # Trust those numbers
127: 
128: ![img-5.jpeg](img-5.jpeg)
129: 
130: timoelliott.com
131: 
132: "Yes sir, you can absolutely trust those numbers"
133: # Considerations for data modeling
134: 
135: 1. Represent part of the real world on a computer/digitally (volcanic eruption)²
136: 2. The representation must fulfill an objective (measure the effects of the volcanic eruption on the population)
137: 3. It must be valid within a specific context (validated by volcanologist experts)
138: 4. The representation must follow a logical scheme (ER model)
139: 5. It must be implemented in some language/framework/system (DBMS)
140: # About the objective of modeling
141: 
142: - Defining the problem and establishing the objective are central elements of data modeling. In business, these are always linked to the goals of the company/organization
143: - The formulation of the objective affects all other modeling considerations
144: - The objective describes the overall result that the modeling aims to achieve
145: - Modeling can have various objectives (represented by business indicators/metrics)
146: # Diagrams showing how data is stored
147: 
148: ![img-6.jpeg](img-6.jpeg)
149: 
150: ![img-7.jpeg](img-7.jpeg)
151: 
152: ![img-8.jpeg](img-8.jpeg)
153: 
154: ![img-9.jpeg](img-9.jpeg)
155: # Considerations at the collection stage
156: 
157: - Needs: Identify the type of data needed and how it will be used to support the modeling objectives
158: - Criteria: Determine the amount of data needed and specify performance criteria to measure quality (usefulness, variability, completeness, uncertainty, etc.)
159: - Collection: Describe how and where data will be obtained (including existing data) and identify any constraints on data collection
160: - Define spatial and temporal boundaries. Thinking in linked data
161: # Primary and secondary data
162: 
163: - Primary data → data constructed by experts on the phenomenon to be studied. E.g., the Iris dataset. In companies they are generally used to build KPIs
164: - Secondary data → statistics not collected for the study of the phenomenon
165: 
166: - The use of secondary data can reveal complementary interesting information, for example, credit card consumption patterns after an earthquake
167: - A large part of the effort should be concentrated on the collection of secondary data
168: - Generally to measure secondary or peripheral indicators
169: - Again, thinking in linked data
170: # Multidimensional data
171: 
172: - A multidimensional dataset is a dataset that contains multiple attributes (or dimensions) that describe each data point or record
173: - Dimensions can represent different aspects of the data, such as time (temporal dimension), location (spatial dimension), categorical labels, numerical values, or other relevant features (analysis dimension)
174: 
175: |  date | IDstation | IDVolcano | lon,lat | pH | crater | magma  |
176: | --- | --- | --- | --- | --- | --- | --- |
177: |  04/03/2013 | 6000890 | vol1 | (12,3) | 14 | 12 | 13  |
178: |  04/03/2013 | 6001950 | vol2 | (4,64) | 16 | 10 | 13  |
179: |  04/03/2013 | 6002122 | vol2 | (93,5) | 10 | 12 | -  |
180: |  08/04/2013 | 6000890 | vol1 | (12,3) | 16 | 10 | 13  |
181: |  08/04/2013 | 6001950 | vol2 | (4,64) | 12 | - | -  |
182: |  08/04/2013 | 6002122 | vol2 | (93,5) | 14 | - | 13  |
183: # Sampling process
184: 
185: - The sampling process consists of selecting those elements from which data will be collected
186: - Census: of each member of the population
187: - Sample: a portion of the population
188: - Recommended reading: The Handbook on Data Collection. Afrialliance³
189: 
190: ³https://afrialliance.org/files/downloads/2019-03/AfriAlliance_Handbook_on_data_collection_2018_ENG.pdf
191: # Quality of data
192: 
193: - Quality data: data with slight bias or error. Bias: systematic error in a data set
194: - Reliability: whether a particular technique, applied repeatedly, gives the same result
195: - Validity: the degree to which an empirical measure adequately reflects the true meaning of the concept under study
196: - Other metrics, such as Timeliness, Completeness and Correctness, are discussed in the literature
197: - It is important to know how the data were collected, particularly for secondary data. For example, the number of inhabitants in a city may have changed
198: # Scientific applications and data science
199: 
200: Theory-driven data science explores the knowledge discovery space that extensively uses available data while looking at the underlying scientific knowledge⁴
201: 
202: ![img-10.jpeg](img-10.jpeg)
203: 
204: ⁴ Anuj Karpatne et al. Theory-guided Data Science: A New Paradigm for Scientific Discovery from Data. arXiv, nov. 2017
205: # Data science models (basic) taxonomy
206: 
207: ![img-11.jpeg](img-11.jpeg)
208: 
209: Antonio, N., de Almeida, A., & Nunes, L. (2022). Data mining and predictive analytics for e-tourism. In Handbook of e-Tourism (pp. 531-555). Cham: Springer International
210: Thank you for your attention!
211: 
