# Programing for Data Science

Phenomena and data

Hugo Alatrista-Salas

hugo.alatrista_salas@devinci.fr

*De Vinci Higher Education, La Défense, Paris*
# Motivation
# Phenomenon: volcanic eruption

# Volcanic Earthquakes

![img-1.jpeg](img-1.jpeg)
# Facts about a volcanic eruption

|  Year | Month | Day | TSU | EQ | Name | Location | Country | Latitude | Longitude | Elevation | Type | Status | Time | VEI | Agent | DEATHS  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  DEATHS | DESCRIPTION |  | MISSING |  | MISSING | DESCRIPTION |  | INJURIES |  | DAMAGE | MILLIONS | DOLLARS |  | HOUSES | DESTROYED |   |
|  HOUSES | DESTROYED | DESCRIPTION |  | TOTAL | DEATHS | TOTAL | DEATHS | DESCRIPTION | TOTAL | MISSING | DESCRIPTION | TOTAL | INJURIES | TOTAL | INJURIES | DESCRIPTION  |
|  |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|  |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
|  TOTAL | DAMAGE | MILLIONS | DOLLARS |  | TOTAL | DAMAGE | DESCRIPTION | TOTAL | HOUSES | DESTROYED | TOTAL | HOUSES | DESTROYED | TOTAL | INJURIES | DESCRIPTION  |
|  -4360 |  |  |  |  | Macaulay Island | Kermadec Is |  | New Zealand | -30.2 | -178.47 | 238 | Caldera Holocene |  | U | 6 |   |
|  -4350 |  |  |  |  | Kikai Ryukyu Is | Japan | 30.78 | 130.28 | 717 | Caldera | Historical | D1 | 7 | P | 3 |   |
|  -4050 |  |  | 3 |  | Masaya Nicaragua | Nicaragua |  | 11.984 | -86.161 | 635 | Caldera | Historical | D1 | 6 |  |   |
|  -4000 |  |  |  |  | Pago New Britain-SW Pac |  |  | Papua New Guinea |  | -5.58 | 150.52 | 742 | Caldera | Historical | D2 | 6  |
|  -3580 | 1 |  |  |  | Taal Luzon-Philippines |  |  | Philippines | 14.002 | 120.993 | 400 | Stratovolcano | Historical |  | D1 | 6  |
|  -3550 |  |  |  |  | Pinatubo Luzon-Philippines |  |  | Philippines | 15.13 | 120.35 | 1486 | Stratovolcano | Historical |  | D1 | 6  |
|  -2040 |  |  |  |  | Long Island New Guinea-NE of |  |  | Papua New Guinea |  | -5.358 | 147.12 | 1280 | Complex volcano | Historical |  | D1 6  |
|  -1900 |  |  |  |  | Black Peak Alaska Peninsula |  |  | United States | 56.53 | -158.8 | 1032 | Stratovolcano | Radiocarbon |  | D7 | 6  |
|  -1860 |  |  |  |  | St. Helens US-Washington |  |  | United States | 46.2 | -122.18 | 2549 | Stratovolcano | Historical |  | D1 | 6  |
|  -1750 |  |  |  |  | Veniaminof Alaska Peninsula |  |  | United States | 56.17 | -159.38 | 2507 | Stratovolcano | Historical |  | D1 | 6  |
|  -1645 |  |  |  |  | Aniakchak Alaska Peninsula |  |  | United States | 56.88 | -158.17 | 1341 | Caldera | Historical |  | D2 | 6  |
|  -1610 |  |  | TSU | EQ | Santorini Greece | Greece | 36.404 | 25.396 | 329 | Shield volcano | Historical | D2 | 6 | W |  |   |
|  -1550 |  |  | TSU |  | Redoubt Alaska-SW |  |  | United States | 60.48 | -152.75 | 3108 | Stratovolcano | Historical |  | D1 |   |
|  -1460 |  |  |  |  | Taupo New Zealand |  |  | New Zealand | -38.82 | 176 | 760 | Caldera | Radiocarbon |  | D6 | 6  |
# Modeling of phenomena
# Representation of the world

![img-2.jpeg](img-2.jpeg)

Sabina Leonelli. What distinguishes data from models? European Journal for Philosophy of Science, Springer, Jan 2019.
# VOLCANO ANATOMY

A network of a replicate in this room of a planetary mass object, such as Earth, that allows hot lava,
soft ash, ash, and gases to escape from a magma chamber before this surface.

![img-4.jpeg](img-4.jpeg)
# Objects, attributes and data (1)

- The world can be represented by a collection of objects and the attributes that describe them
- An attribute is a property or characteristic of an object

- E.g., person's eye color or temperature.
- Attributes are also known as variables, fields, or characteristics

- Collections of attributes describe an object
- Objects may or may not belong to a class

- Certain characteristics of an object may determine the class to which it belong
- Classes can range from two (binary) to more (multi-class)

- An instance of an object is known as a record, point, entity, or individual.
# Objects, attributes and data (2)

- Data or attribute values are numbers or symbols assigned to an attribute or characteristic of an object
- Differences between attributes and data (or attribute values)

- A piece of data can take different values, but they generally respond to only one type. For example, distance can be measured in feet or meters. Feet can be integers and meters can be real numbers
- Different attributes can be assigned to the same data domain; for example, the values for the number of children and age are integers. The age domain is an integer value between 0 and 120.
- Data domains can differ. For example, ID has no limit, but age has a maximum and minimum value
# Nominal and Ordinal Attributes

- Nominal: categories, states, or names of things

- e.g., days of the week = Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday
- Other examples are marital status, occupation, ID, eye color, etc.

- Ordinal: values that imply an order (ranking)

- The magnitude between successive values is unknown
- e.g., size = small, medium, large
- e.g., evaluation of the acceptance of Lay's Chips (scale of 1-10)
# Binary attributes

- They are nominal attributes with only two states, e.g., 0 and 1
- Symmetric binaries: both values have the same importance, e.g., sex = {male, female}
- Asymmetric binaries: not symmetric. e.g., medical tests positive, negative
- By convention, we assign a value of 1 to the most important item (e.g., an infected patient or a satisfied customer)
# Discrete and Continuous Attributes

- Discrete (categorical) attributes

- Have only finite values, e.g., telephone numbers, letters in a document, professions, etc.
- Sometimes represented by an integer value
- Note: binary attributes are a particular type of discrete attribute

- Continuous attributes

- Have real numbers as attribute values, e.g., temperature, weight, height, etc.
- Are typically represented by floating-point numbers. In practice, values can be represented by a finite number of digits
# Exercises

1. Data scientists at the bank are interested in studying the credit risk of their clients. Give two examples of binary attributes (with their possible values), two discrete attributes and two continuous attributes that can be used in this study
2. A questionnaire is associated with the study of our clients, and the following attributes are taken into account: a) age, b) sex, c) profession, d) height, and e) number of children. Indicate the types of data used for each attribute
3. An employee notes the order in which clients pay their debts. The first one has already paid, the second one, ... Which type of attributes are being used?
4. In the marketing area, a study is being carried out on clients' perceptions of the totems annonces used by a bank. The idea is to analyze facial expressions captured by a camera and determine the polarity in the expressions of the individuals studied. What attribute type will be used and what values can this attribute have?
5. The aim is to study the impact of temperature on the purchasing habits of the bank's clients. The data is collected daily for a year. How would you group the data so that it is binary? For example, I group it by quarter but the attribute is not binary, but nominal
# Answers

1. Binary: sex (male, female), debtor (yes, no), has a card (yes, no), etc.
   Discrete: number of children, number of cards, etc.
   Continuous: balance in your account, APR of your last loan, etc.
2. There are many ways to answer this question. Discrete a), c) and d), continuous d), binary b)
3. Ordinal
4. Nominal, with positive, neutral and negative values
5. Period={summer season, cold season}
# Data modeling
# Representation of phenomena with data

Data captures and conveys the same information about the world, regardless of the circumstances of the research and, in particular, the assumptions and backgrounds of the researchers who use it as evidence¹.

¹Sabina Leonelli. What distinguishes data from models? European Journal for Philosophy of Science, Springer, Jan 2019.
# Trust those numbers

![img-5.jpeg](img-5.jpeg)

timoelliott.com

"Yes sir, you can absolutely trust those numbers"
# Considerations for data modeling

1. Represent part of the real world on a computer/digitally (volcanic eruption)²
2. The representation must fulfill an objective (measure the effects of the volcanic eruption on the population)
3. It must be valid within a specific context (validated by volcanologist experts)
4. The representation must follow a logical scheme (ER model)
5. It must be implemented in some language/framework/system (DBMS)
# About the objective of modeling

- Defining the problem and establishing the objective are central elements of data modeling. In business, these are always linked to the goals of the company/organization
- The formulation of the objective affects all other modeling considerations
- The objective describes the overall result that the modeling aims to achieve
- Modeling can have various objectives (represented by business indicators/metrics)
# Diagrams showing how data is stored

![img-6.jpeg](img-6.jpeg)

![img-7.jpeg](img-7.jpeg)

![img-8.jpeg](img-8.jpeg)

![img-9.jpeg](img-9.jpeg)
# Considerations at the collection stage

- Needs: Identify the type of data needed and how it will be used to support the modeling objectives
- Criteria: Determine the amount of data needed and specify performance criteria to measure quality (usefulness, variability, completeness, uncertainty, etc.)
- Collection: Describe how and where data will be obtained (including existing data) and identify any constraints on data collection
- Define spatial and temporal boundaries. Thinking in linked data
# Primary and secondary data

- Primary data → data constructed by experts on the phenomenon to be studied. E.g., the Iris dataset. In companies they are generally used to build KPIs
- Secondary data → statistics not collected for the study of the phenomenon

- The use of secondary data can reveal complementary interesting information, for example, credit card consumption patterns after an earthquake
- A large part of the effort should be concentrated on the collection of secondary data
- Generally to measure secondary or peripheral indicators
- Again, thinking in linked data
# Multidimensional data

- A multidimensional dataset is a dataset that contains multiple attributes (or dimensions) that describe each data point or record
- Dimensions can represent different aspects of the data, such as time (temporal dimension), location (spatial dimension), categorical labels, numerical values, or other relevant features (analysis dimension)

|  date | IDstation | IDVolcano | lon,lat | pH | crater | magma  |
| --- | --- | --- | --- | --- | --- | --- |
|  04/03/2013 | 6000890 | vol1 | (12,3) | 14 | 12 | 13  |
|  04/03/2013 | 6001950 | vol2 | (4,64) | 16 | 10 | 13  |
|  04/03/2013 | 6002122 | vol2 | (93,5) | 10 | 12 | -  |
|  08/04/2013 | 6000890 | vol1 | (12,3) | 16 | 10 | 13  |
|  08/04/2013 | 6001950 | vol2 | (4,64) | 12 | - | -  |
|  08/04/2013 | 6002122 | vol2 | (93,5) | 14 | - | 13  |
# Sampling process

- The sampling process consists of selecting those elements from which data will be collected
- Census: of each member of the population
- Sample: a portion of the population
- Recommended reading: The Handbook on Data Collection. Afrialliance³

³https://afrialliance.org/files/downloads/2019-03/AfriAlliance_Handbook_on_data_collection_2018_ENG.pdf
# Quality of data

- Quality data: data with slight bias or error. Bias: systematic error in a data set
- Reliability: whether a particular technique, applied repeatedly, gives the same result
- Validity: the degree to which an empirical measure adequately reflects the true meaning of the concept under study
- Other metrics, such as Timeliness, Completeness and Correctness, are discussed in the literature
- It is important to know how the data were collected, particularly for secondary data. For example, the number of inhabitants in a city may have changed
# Scientific applications and data science

Theory-driven data science explores the knowledge discovery space that extensively uses available data while looking at the underlying scientific knowledge⁴

![img-10.jpeg](img-10.jpeg)

⁴ Anuj Karpatne et al. Theory-guided Data Science: A New Paradigm for Scientific Discovery from Data. arXiv, nov. 2017
# Data science models (basic) taxonomy

![img-11.jpeg](img-11.jpeg)

Antonio, N., de Almeida, A., & Nunes, L. (2022). Data mining and predictive analytics for e-tourism. In Handbook of e-Tourism (pp. 531-555). Cham: Springer International
Thank you for your attention!

