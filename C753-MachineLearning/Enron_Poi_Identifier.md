# Person of Interest Identification as an Introduction to Machine Learning

The dataset resulting from the bankruptcy of Enron presents an opportunity for supervised machine learning. We know who the persons of interest are in this dataset. Having labels for the feature sets allows us to gauge the accuracy of any classifier we train. By comparing the number of accurately identified feature sets between classifier configurations we can determine techniques for classifier creation. These techniques can then be adapted to scenarios where we are less lucky and do not have labels for our feature sets. That is the goal of this project, building some technique for accurate classifier training through supervised machine learning.  

## Initial Data Investigation

As with any investigation, we'll start with some high level understanding of the dataset we have and the features it contains.  

The data we're beginning with has been provided as the file final_project_dataset.py. It contains a serialized dictionary of dictionaries. The keys in the parent dictionary refer to a person. The child dictionary returned for each person contains the features of interest. A little bit of scripting with explore_enron_data.py will help us get a better handle on some of the detail of this dataset.

Also provided was a manual data scrape of a USA Today article providing names of people of interest. Comparing that list with the source article uncovers some questionable names. Christopher Loehr does not appear in the article. His absence from the article makes his inclusion questionable. A search shows he had some involvement but turned state's evidence, so his inclusion as a poi is warranted. There's also names in source article missing from the list. David Duncan and Arthur Andersen both destroyed evidence and had charges that were removed due to lack of criminal intent. There's argument for each of these names to be labeled as poi or not. With Loehr having involvement, he should be labeled as a poi despite his absence from the article. Andersen and Duncan's exclusion will also stand as it is not clear their roles in the fraud fit the definition of poi.

A little scripting gets us some deeper insight to the data.

```{python}
Count of entries in dataset: 146
Count of features in dataset: 21
Number of features not assigned to everyone: 0
Number of POI already labeled in dataset: 18
Number of POI identified in manual scrape: 35
Number of POI from all sources: 35
Number of POI not in dataset: 17
Number of POI in dataset and not labeled: 0
```

All 146 people in the dataset have a key for each of the 21 unique features in the dataset.
All identified people of interest in the dataset have been labeled as poi.
Not all identified poi are in the dataset.

On this initial pass of data investigation, some name cleaning was applied. Single characters (initials), periods and the specific title JR were removed. On a closer inspection, there's some names that don't make sense. Some additional cleaning may be in order.  

```{python}
***Entries With More Than Two Names***

PEREIRA PAULO FERRAZ
{'deferred_income': -101250,
 'director_fees': 101250,
 'expenses': 27942,
 'poi': False,
 'total_payments': 27942}

THE TRAVEL AGENCY IN THE PARK
{'other': 362096, 'poi': False, 'total_payments': 362096}
```

Both of these entries are very curious.

Paulo Ferraz Pereira raises the question of deferred income. Movement of funds from deferred compensation accounts to limited partnerships prior to the bankruptcy was one of the more scandalous behaviors. The practice resulted in a new law, Section 409A of the Internal Revenue Code. The provided pdf is the source of the financial data. It defines deferred_income as: "Reflects voluntary executive deferrals of salary, annual cash incentives, and long-term cash incentives as well as cash fees deferred by non-employee directors under a deferred compensation arrangement.  May also reflect deferrals under a stock option or phantom stock unit in lieu of cash arrangement." With this definition and the need for more regulation, deferred payments seem to have been common enough practice. Having more than 2 names doesn't disqualify the entry from inclusion.

Travel Agency in the Park is a different animal. Despite the court decision of Citizen's United, it is not a person. It even has it's own footnote on the financial dataset. "Payments were made by Enron employees on account of business-related travel to The Travel Agency in the Park (later Alliance Worldwide), which was coowned by the sister of Enron's former Chairman.  Payments made by the Debtor to reimburse employees for these expenses have not been included." Aside from having more than two names, it also only has 2 non-NaN features (the poi field is a label). Who else in the dataset can be described by this?  

```
***Entries With Two or Fewer Features***

WHALEY DAVID
{'exercised_stock_options': 98718, 'poi': False, 'total_stock_value': 98718}

WROBEL BRUCE
{'exercised_stock_options': 139130, 'poi': False, 'total_stock_value': 139130}

LOCKHART EUGENE
{'poi': False}

GRAMM WENDY
{'director_fees': 119292, 'poi': False, 'total_payments': 119292}

THE TRAVEL AGENCY IN THE PARK
{'other': 362096, 'poi': False, 'total_payments': 362096}
```

Of those with 2 or fewer features, only Eugene Lockhart stands out as an oddity. There doesn't appear to be an email dump associated with him. He doesn't appear in the financial spreadsheet. There's no apparent reason for him to exist in this dataset. Some research into who is Eugene Lockhart suggests he's the CEO of a failed energy startup in the energy supply market; "New Power Company". That seems more plausible than the former Dallas Cowboy linebacker. "The New Power Company" may have some involvement in the Enron scandal, but data from that company doesn't seem to be included in our dataset. With the information available, the Eugene Lockhart in the dataset could be the former footballer.  

Based on these findings, there's two entries that can be completely dropped from dataset. "The Travel Agency in the Park" by name and "Eugene Lockhart" by lacking features. For the remaining data points, their features could use a bit more scrutiny.  

## Deeper Data exploration

```{python}
***Types in use for features***
{'bonus': set(['int']),
 'deferral_payments': set(['int']),
 'deferred_income': set(['int']),
 'director_fees': set(['int']),
 'email_address': set(['str']),
 'exercised_stock_options': set(['int']),
 'expenses': set(['int']),
 'from_messages': set(['int']),
 'from_poi_to_this_person': set(['int']),
 'from_this_person_to_poi': set(['int']),
 'loan_advances': set(['int']),
 'long_term_incentive': set(['int']),
 'other': set(['int']),
 'poi': set(['bool']),
 'restricted_stock': set(['int']),
 'restricted_stock_deferred': set(['int']),
 'salary': set(['int']),
 'shared_receipt_with_poi': set(['int']),
 'to_messages': set(['int']),
 'total_payments': set(['int']),
 'total_stock_value': set(['int'])}
```

At the least, the dataset is consistent in its use of stored data. Aside from the poi boolean and email_address string, everything is numerical. There's also no mixing of numerical types. If it's not the poi label or email address, it is an integer.  

```{python}
***Number of entries with valued feature***
{'bonus': 82,
 'deferral_payments': 39,
 'deferred_income': 49,
 'director_fees': 17,
 'email_address': 111,
 'exercised_stock_options': 102,
 'expenses': 95,
 'from_messages': 86,
 'from_poi_to_this_person': 86,
 'from_this_person_to_poi': 86,
 'loan_advances': 4,
 'long_term_incentive': 66,
 'other': 93,
 'poi': 146,
 'restricted_stock': 110,
 'restricted_stock_deferred': 18,
 'salary': 95,
 'shared_receipt_with_poi': 86,
 'to_messages': 86,
 'total_payments': 125,
 'total_stock_value': 126}
```

The inclusion of loan_advances is questionable. With only 4 data points, there's a good chance this data would only skew results. Looking at the financial data source, Kenneth Lay utilized these loan advances to dump his stock holdings back on the company. It also explains why his total payment is astronomical compared to everyone else. The other entries with loan advances are Mark Frevert and Mark Pickering. Between the three of them, Frevert and Lay are known POI. This suggests loan_advances is a feature that will introduce a non-insignificant amount of bias to our model.  

To deal with this biased feature, my first thought is to completely remove loan_advances from the data set and adjust the total_payments feature accordingly. This would effectively remove any bias it introduces. I'm not comfortable with this idea of ignoring a feature due to introduction of implicit bias. Ignoring a feature due to implicit bias may have an effect of shifting the bias to other features where it is less apparent. A better method would have the machine determine how much bias exists within this feature and weigh it accordingly. Such a technique would allow us to include a strong identifier of people of interest.

Despite my concerns over removing the loan_advances feature, I have to admit that its data population is sparse. The majority of persons of interest do not have this field populated. Comparing classifiers trained with and without this field would be a matter of academic curiosity. Academic curiosity is tangential to this project. To maintain the scope of this project, I will be removing the feature and adjusting the total payments accordingly.  

Before moving on to the rest of the features, we cannot ignore the discrepancy in counts. We found only three persons in the data source with loan_advances. Our dataset claims to have four. Who is the fourth?  

```{python}
***Entries with loan_advances***
set(['FREVERT MARK', 'LAY KENNETH', 'PICKERING MARK', 'TOTAL'])
```

Seems there's an additional entry that needs to be dropped. More than two names and two or less features would not catch someone with one name and all financial features. The "TOTAL" entry will be added to the entries that need to be scrubbed from the dataset.  

### Feature Details

To finish the data exploration, we'll look at general feature details. The features fit into two categories defined by their source. The financial information comes from the spreadsheet showing who was paid what and how. The features scraped from the email dump are raw counts of email interactions with persons of interest. The inclusion and value of these counts are questionable to me.

At this point, data_prep.py has been ran and the cleaned dataset is being investigated. This data has been loaded

#### Financial Features

* Salary
* Deferral_payments
* Total_payments
* loan_advances
* Bonus
* Restricted_stock_deferred
* Deferred_income
* Total_stock_value
* Expenses
* Exercised_stock_options
* Other
* Long_term_incentive
* Restricted_stock
* Director_fees

#### Communicative Features

* To_messages
* Email_address
* From_poi_to_this_person
* From_messages
* From_this_person_to_poi
* Shared_receipt_with_poi

I've taken the cleaned dataset and loaded it into dataframes for some basic statistics.

```{Python}
         salary  deferral_payments  total_payments      bonus  restricted_stock_deferred  deferred_income  total_stock_value  expenses  exercised_stock_options       other  long_term_incentive  restricted_stock  director_fees
count     143.00             143.00          143.00     143.00                     143.00           143.00             143.00    143.00                   143.00      143.00               143.00            143.00         143.00
mean   186742.86          223642.63      1685434.48  680724.61                   73931.31       -195037.70         2930133.76  35622.72               2090318.08   296806.69            339314.18         874609.97       10050.11
std    197117.07          756520.79      2925088.47 1236179.69                 1306545.17        607922.47         6205936.52  45370.87               4809193.25  1135030.65            689013.93        2022338.37       31399.35
min         0.00         -102500.00            0.00       0.00                -1787380.00      -3504386.00          -44093.00      0.00                     0.00        0.00                 0.00       -2604490.00           0.00
25%         0.00               0.00        96796.50       0.00                       0.00        -37506.00          254936.00      0.00                     0.00        0.00                 0.00          38276.50           0.00
50%    210692.00               0.00       966522.00  300000.00                       0.00             0.00          976037.00  21530.00                608750.00      947.00                 0.00         360528.00           0.00
75%    270259.00            9110.00      1956977.50  800000.00                       0.00             0.00         2307583.50  53534.50               1698900.50   149204.00            374825.50         775992.00           0.00
max   1111258.00         6426990.00     22034793.00 8000000.00                15456290.00             0.00        49110078.00 228763.00              34348384.00 10359729.00           5145434.00       14761694.00      137864.00
       to_messages  from_poi_to_this_person  from_messages  from_this_person_to_poi  shared_receipt_with_poi
count        86.00                    86.00          86.00                    86.00                    86.00
mean       2073.86                    64.90         608.79                    41.23                  1176.47
std        2582.70                    86.98        1841.03                   100.07                  1178.32
min          57.00                     0.00          12.00                     0.00                     2.00
25%         541.25                    10.00          22.75                     1.00                   249.75
50%        1211.00                    35.00          41.00                     8.00                   740.50
75%        2634.75                    72.25         145.50                    24.75                  1888.25
max       15149.00                   528.00       14368.00                   609.00                  5521.00
```

The first thing to jump out at me are all the zeros in the financial dataset. The financial datasource has a lot of 'NaN' values. The default behavior of the feature selector is to change 'NaN' values to 0. This introduction of zeros could skew the data. Handling of null data needs to be weighed.

```{Python}
          salary  deferral_payments  total_payments      bonus  restricted_stock_deferred  deferred_income  total_stock_value  expenses  exercised_stock_options       other  long_term_incentive  restricted_stock  director_fees
count      94.00              38.00          123.00      81.00                      17.00            48.00             125.00     94.00                   101.00       91.00                65.00            109.00          16.00
mean   284087.54          841602.53      1959488.86 1201773.07                  621892.82       -581049.81         3352073.02  54192.01               2959559.26   466410.52            746491.20        1147424.09       89822.88
std    177131.12         1289322.63      3068775.11 1441679.44                 3845528.35        942076.40         6532883.10  46108.38               5499449.60  1397375.61            862917.42        2249770.36       41112.70
min       477.00         -102500.00          148.00   70000.00                -1787380.00      -3504386.00          -44093.00    148.00                  3285.00        2.00             69223.00       -2604490.00        3285.00
25%    211802.00           79644.50       396934.00  425000.00                 -329825.00       -611209.25          494136.00  22479.00                506765.00     1203.00            275000.00         252055.00       83674.50
50%    258741.00          221063.50      1099100.00  750000.00                 -140264.00       -151927.00         1095040.00  46547.50               1297049.00    51587.00            422158.00         441096.00      106164.50
75%    308606.50          867211.25      2087529.50 1200000.00                  -72419.00        -37926.00         2606763.00  78408.50               2542813.00   331983.00            831809.00         985032.00      112815.00
max   1111258.00         6426990.00     22034793.00 8000000.00                15456290.00          -833.00        49110078.00 228763.00              34348384.00 10359729.00           5145434.00       14761694.00      137864.00
       to_messages  from_poi_to_this_person  from_messages  from_this_person_to_poi  shared_receipt_with_poi
count        86.00                    86.00          86.00                    86.00                    86.00
mean       2073.86                    64.90         608.79                    41.23                  1176.47
std        2582.70                    86.98        1841.03                   100.07                  1178.32
min          57.00                     0.00          12.00                     0.00                     2.00
25%         541.25                    10.00          22.75                     1.00                   249.75
50%        1211.00                    35.00          41.00                     8.00                   740.50
75%        2634.75                    72.25         145.50                    24.75                  1888.25
max       15149.00                   528.00       14368.00                   609.00                  5521.00
```

Changing this behavior of the feature selector script has a great effect on the statistics of the financial data and no effect on the email data. This is due to the feature selector's default behavior of removing all data points with all zeros. This is strange because our previous counts show there's 111 data points with email addresses and there's only 86 with email statistics. What's the story for these 25 other email addresses?

```{Python}
111 email addresses counted
***Number of email stats for persons with email addresses***
{'ALLEN PHILLIP': 5,
 'BANNANTINE JAMES': 5,
 'BAY FRANKLIN': 0,
 'BECK SALLY': 5,
 'BELDEN TIMOTHY': 5,
 'BERBERIAN DAVID': 0,
 'BERGSIEKER RICHARD': 5,
 'BHATNAGAR SANJAY': 5,
 'BIBI PHILIPPE': 5,
 'BLACHMAN JEREMY': 5,
 'BOWEN RAYMOND': 5,
 'BROWN MICHAEL': 5,
 'BUCHANAN HAROLD': 5,
 'BUTTS ROBERT': 0,
 'BUY RICHARD': 5,
 'CALGER CHRISTOPHER': 5,
 'CARTER REBECCA': 5,
 'CAUSEY RICHARD': 5,
 'CHRISTODOULOU DIOMEDES': 0,
 'COLWELL WESLEY': 5,
 'CORDES WILLIAM': 5,
 'COX DAVID': 5,
 'DEFFNER JOSEPH': 5,
 'DELAINEY DAVID': 5,
 'DERRICK JAMES': 5,
 'DETMERING TIMOTHY': 0,
 'DIETRICH JANET': 5,
 'DIMICHELE RICHARD': 0,
 'DODSON KEITH': 5,
 'DONAHUE JEFFREY': 5,
 'DURAN WILLIAM': 5,
 'ECHOLS JOHN': 0,
 'ELLIOTT STEVEN': 0,
 'FALLON JAMES': 5,
 'FASTOW ANDREW': 0,
 'FITZGERALD JAY': 5,
 'FOWLER PEGGY': 5,
 'FOY JOE': 5,
 'FREVERT MARK': 5,
 'GARLAND KEVIN': 5,
 'GIBBS DANA': 5,
 'GLISAN BEN': 5,
 'GOLD JOSEPH': 0,
 'HAEDICKE MARK': 5,
 'HANNON KEVIN': 5,
 'HAUG DAVID': 5,
 'HAYES ROBERT': 5,
 'HAYSLETT RODERICK': 5,
 'HERMANN ROBERT': 0,
 'HICKERSON GARY': 5,
 'HIRKO JOSEPH': 0,
 'HORTON STANLEY': 5,
 'HUGHES JAMES': 5,
 'HUMPHREY GENE': 5,
 'IZZO LAWRENCE': 5,
 'JACKSON CHARLENE': 5,
 'KAMINSKI WINCENTY': 5,
 'KEAN STEVEN': 5,
 'KISHKILL JOSEPH': 0,
 'KITCHEN LOUISE': 5,
 'KOENIG MARK': 5,
 'KOPPER MICHAEL': 0,
 'LAVORATO JOHN': 5,
 'LAY KENNETH': 5,
 'LEFF DANIEL': 5,
 'LEWIS RICHARD': 5,
 'LINDHOLM TOD': 0,
 'MARTIN AMANDA': 5,
 'MCCARTY DANNY': 5,
 'MCCLELLAN GEORGE': 5,
 'MCCONNELL MICHAEL': 5,
 'MCDONALD REBECCA': 5,
 'MCMAHON JEFFREY': 5,
 'METTS MARK': 5,
 'MEYER ROCKFORD': 5,
 'MORAN MICHAEL': 5,
 'MORDAUNT KRISTINA': 0,
 'MULLER MARK': 5,
 'MURRAY JULIA': 5,
 'OLSON CINDY': 5,
 'OVERDYKE JERE': 0,
 'SKILLING JEFFREY': 5,
 'STABLER FRANK': 0,
 'SUNDE MARTIN': 5,
 'TAYLOR MITCHELL': 5,
 'THORN TERENCE': 5,
 'TILNEY ELIZABETH': 5,
 'UMANOFF ADAM': 5,
 'WALLS ROBERT': 5,
 'WASAFF GEORGE': 5,
 'WESTFAHL RICHARD': 0,
 'WHALLEY LAWRENCE': 5,
 'WHITE THOMAS': 0,
 'WODRASKA JOHN': 0,
 'YEAGER SCOTT': 0}
```

It seems those with email statistics have all 5 email statistics. So what about these that have none? From a quick manual scan of the email dump, there isn't any overt correlation between the email dump and the persons that make up our data points. The best theory I have is some email header parser was used to create these counts. So it remains a mystery how this data was obtained. Recreating such a parser is out of scope for this project. Tt would just be best to either take these values at face value or outright reject them. So far I have no reason to reject these counts.

One insight into what email data was chosen to be included is by investigating the intersection between financial and email data. On each data point ask if it has email statistics, financial data or both. The one data point with no financial and no email data (Eugene Lockhart) has already been scrubbed from the dataset.

I've added a set of booleans to the dataset to provide a handle on this intersection.  

```{Python}
***Persons with both Financial and Email data***
set(['ALLEN PHILLIP',
     'BANNANTINE JAMES',
     'BECK SALLY',
     'BELDEN TIMOTHY',
     'BERGSIEKER RICHARD',
     'BHATNAGAR SANJAY',
     'BIBI PHILIPPE',
     'BLACHMAN JEREMY',
     'BOWEN RAYMOND',
     'BROWN MICHAEL',
     'BUCHANAN HAROLD',
     'BUY RICHARD',
     'CALGER CHRISTOPHER',
     'CARTER REBECCA',
     'CAUSEY RICHARD',
     'COLWELL WESLEY',
     'CORDES WILLIAM',
     'COX DAVID',
     'DEFFNER JOSEPH',
     'DELAINEY DAVID',
     'DERRICK JAMES',
     'DIETRICH JANET',
     'DODSON KEITH',
     'DONAHUE JEFFREY',
     'DURAN WILLIAM',
     'FALLON JAMES',
     'FITZGERALD JAY',
     'FOWLER PEGGY',
     'FOY JOE',
     'FREVERT MARK',
     'GARLAND KEVIN',
     'GIBBS DANA',
     'GLISAN BEN',
     'HAEDICKE MARK',
     'HANNON KEVIN',
     'HAUG DAVID',
     'HAYES ROBERT',
     'HAYSLETT RODERICK',
     'HICKERSON GARY',
     'HORTON STANLEY',
     'HUGHES JAMES',
     'HUMPHREY GENE',
     'IZZO LAWRENCE',
     'JACKSON CHARLENE',
     'KAMINSKI WINCENTY',
     'KEAN STEVEN',
     'KITCHEN LOUISE',
     'KOENIG MARK',
     'LAVORATO JOHN',
     'LAY KENNETH',
     'LEFF DANIEL',
     'LEWIS RICHARD',
     'MARTIN AMANDA',
     'MCCARTY DANNY',
     'MCCLELLAN GEORGE',
     'MCCONNELL MICHAEL',
     'MCDONALD REBECCA',
     'MCMAHON JEFFREY',
     'METTS MARK',
     'MEYER ROCKFORD',
     'MORAN MICHAEL',
     'MULLER MARK',
     'MURRAY JULIA',
     'OLSON CINDY',
     'PICKERING MARK',
     'PIPER GREGORY',
     'PIRO JIM',
     'POWERS WILLIAM',
     'REDMOND BRIAN',
     'RICE KENNETH',
     'RIEKER PAULA',
     'SHANKMAN JEFFREY',
     'SHAPIRO RICHARD',
     'SHARP VICTORIA',
     'SHELBY REX',
     'SHERRICK JEFFREY',
     'SHERRIFF JOHN',
     'SKILLING JEFFREY',
     'SUNDE MARTIN',
     'TAYLOR MITCHELL',
     'THORN TERENCE',
     'TILNEY ELIZABETH',
     'UMANOFF ADAM',
     'WALLS ROBERT',
     'WASAFF GEORGE',
     'WHALLEY LAWRENCE'])

***Persons with only Email data***
set([])

***Persons with only Financial data***
set(['BADUM JAMES',
     'BAXTER JOHN',
     'BAY FRANKLIN',
     'BAZELIDES PHILIP',
     'BELFER ROBERT',
     'BERBERIAN DAVID',
     'BLAKE NORMAN',
     'BUTTS ROBERT',
     'CHAN RONNIE',
     'CHRISTODOULOU DIOMEDES',
     'CLINE KENNETH',
     'CUMBERLAND MICHAEL',
     'DETMERING TIMOTHY',
     'DIMICHELE RICHARD',
     'DUNCAN JOHN',
     'ECHOLS JOHN',
     'ELLIOTT STEVEN',
     'FASTOW ANDREW',
     'FUGH JOHN',
     'GAHN ROBERT',
     'REYNOLDS LAWRENCE',
     'SAVAGE FRANK',
     'SCRIMSHAW MATTHEW',
     'STABLER FRANK',
     'SULLIVAN-SHAKLOVITZ COLLEEN',
     'URQUHART JOHN',
     'WAKEHAM JOHN',
     'WALTERS GARETH',
     'WESTFAHL RICHARD',
     'WHALEY DAVID',
     'WHITE THOMAS',
     'WINOKUR HERBERT',
     'WODRASKA JOHN',
     'WROBEL BRUCE',
     'YEAGER SCOTT',
     'YEAP SOON'])

***No elephants should be in cairo***
***Elephants have no values***
set([])
```

All of our data points have some form of financial information but only some have email statistics. The email statistics are more complete than the financial data but the financial data has more observations. "Follow the money" is the saying.  

I am concerned about the null values in the financial data set. A non-zero amount of consideration has been given on how to best handle these. Given the scope of this project, the decision is imputation to zero. Under the assumption that a null value represents money not paid, zero is the only value that could be used. The convience of the provided feature selector code defaulting to imputation as way of handling zeros is also not lost on me.  

Working with the assumptions that finacial data nulls are zeros requires we verify the scaling of the financial data. To review, here again is the statistical summary of the financial data with and without imputation.

```{python}
***Financial Data Summary, including null as zeros***
          salary  deferral_payments  total_payments      bonus  restricted_stock_deferred  deferred_income  ...  expenses  exercised_stock_options       other  long_term_incentive  restricted_stock  director_fees  
count     143.00             143.00          143.00     143.00                     143.00           143.00  ...    143.00                   143.00      143.00               143.00            143.00         143.00  
mean   186742.86          223642.63      1685434.48  680724.61                   73931.31       -195037.70  ...  35622.72               2090318.08   296806.69            339314.18         874609.97       10050.11  
std    197117.07          756520.79      2925088.47 1236179.69                 1306545.17        607922.47  ...  45370.87               4809193.25  1135030.65            689013.93        2022338.37       31399.35  
min         0.00         -102500.00            0.00       0.00                -1787380.00      -3504386.00  ...      0.00                     0.00        0.00                 0.00       -2604490.00           0.00  
25%         0.00               0.00        96796.50       0.00                       0.00        -37506.00  ...      0.00                     0.00        0.00                 0.00          38276.50           0.00  
50%    210692.00               0.00       966522.00  300000.00                       0.00             0.00  ...  21530.00                608750.00      947.00                 0.00         360528.00           0.00  
75%    270259.00            9110.00      1956977.50  800000.00                       0.00             0.00  ...  53534.50               1698900.50   149204.00            374825.50         775992.00           0.00  
max   1111258.00         6426990.00     22034793.00 8000000.00                15456290.00             0.00  ... 228763.00              34348384.00 10359729.00           5145434.00       14761694.00      137864.00  

[8 rows x 13 columns]

***Financial Data Summary, excluding nulls***
          salary  deferral_payments  total_payments      bonus  restricted_stock_deferred  deferred_income  ...  expenses  exercised_stock_options       other  long_term_incentive  restricted_stock  director_fees  
count      94.00              38.00          123.00      81.00                      17.00            48.00  ...     94.00                   101.00       91.00                65.00            109.00          16.00  
mean   284087.54          841602.53      1959488.86 1201773.07                  621892.82       -581049.81  ...  54192.01               2959559.26   466410.52            746491.20        1147424.09       89822.88  
std    177131.12         1289322.63      3068775.11 1441679.44                 3845528.35        942076.40  ...  46108.38               5499449.60  1397375.61            862917.42        2249770.36       41112.70  
min       477.00         -102500.00          148.00   70000.00                -1787380.00      -3504386.00  ...    148.00                  3285.00        2.00             69223.00       -2604490.00        3285.00  
25%    211802.00           79644.50       396934.00  425000.00                 -329825.00       -611209.25  ...  22479.00                506765.00     1203.00            275000.00         252055.00       83674.50  
50%    258741.00          221063.50      1099100.00  750000.00                 -140264.00       -151927.00  ...  46547.50               1297049.00    51587.00            422158.00         441096.00      106164.50  
75%    308606.50          867211.25      2087529.50 1200000.00                  -72419.00        -37926.00  ...  78408.50               2542813.00   331983.00            831809.00         985032.00      112815.00  
max   1111258.00         6426990.00     22034793.00 8000000.00                15456290.00          -833.00  ... 228763.00              34348384.00 10359729.00           5145434.00       14761694.00      137864.00  

[8 rows x 13 columns]
```

The first thing I note are the difference in counts. Some fields have a wide drop in observations. "Restricted Stock Deferred" drops from 143 observations to 17. "Director Fees" drops to only 16 observations. Some of these features are so sparsely populated that they could easily be considered boolean.  

```{Python}
*** Observations % Populated : 13***
salary                      0.66
deferral_payments           0.27
total_payments              0.86
bonus                       0.57
restricted_stock_deferred   0.12
deferred_income             0.34
total_stock_value           0.87
expenses                    0.66
exercised_stock_options     0.71
other                       0.64
long_term_incentive         0.45
restricted_stock            0.76
director_fees               0.11
Name: count, dtype: float64

*** Observations > 50% Populated : 8***
salary                    0.66
total_payments            0.86
bonus                     0.57
total_stock_value         0.87
expenses                  0.66
exercised_stock_options   0.71
other                     0.64
restricted_stock          0.76
Name: count, dtype: float64

*** Observations > 66% Populated : 4***
total_payments            0.86
total_stock_value         0.87
exercised_stock_options   0.71
restricted_stock          0.76
Name: count, dtype: float64

```

Aside from total payments, the most populated features pertain to stocks. Instinctually this should make sense. The scandal was inflating the apparent value of the company through questionable accounting practices (fraud) and cashing in on that appearance. What doesn't make sense are the null total payments. Looking at the spreadsheet, this is quickly cleared up. Stocks are considered part of the financial data but they are not included in the payment calculations. There's people with stocks and no payment data. There's also people with payments that were deferred. That is, money paid on the books but deferred to a later time.

This suggests at least three games being played in the financial dataset; stocks, deferred payments and the previously scrubbed loans. Knowledge or involvement in the fraud would affect how you played each of those games. Participation in each game and the weight of each game towards classification would be the most comprehensive model we could build. The scope of that is greater than what this project demands.

To remain in scope, the over all financial game would best be explored via a model that can handle imputed zeros as booleans for sparsely populated features while not sacrificing the nuance of non-zero values. It would also need to handle features individually so the weight of each feature towards classification could be determined. Adaboost seems to fit this criteria most exactly. As repayment of loans with overvalued stocks is one of the identified games, the previously scrubed loan data should be returned to the dataset. It may be of academic interest to compare the performance of an Adaboost classifier with and without this datapoint.

Another classifier based entirely on the stock game could also be ran. Consideration of the needs of modeling the stock game will be tabled for now.

## Adaboosting financial data

For adjustment, the adaboost module gives us these parameters.

* base_estimator: (default: DecisionTreeClassifier(max_depth=1)) The type of estimator (weak classifiers) to boost. e.g. random forest of stumps
* n_estimators: (default: 50) number of estimators (weak classifiers) to create. Puts a limit on execution by implementing termination
* learning_rate: (default: 1) shrink contribution of subsequent classifiers by this amount.
* algorithm: (default: 'SAMME.R') Two available algorithms for boosting: Real SAMME (SAMME.R) and Discrete SAMME
* random_state: (default: None) Random number generator configuration. None uses what np.random uses.

Of these options, learning_rate and n_estimators seem to be the most pertinent options for accuracy adjustments. As we're dealing with a two class problem, the mulitple class design of descrete SAMME is not necessary. The default SAMME.R should offer better accuracy. Random forest of stumps is exactly what's wanted for this model. It handles each feature as a nuanced boolean that can be weighted into the classification calculation.

### Effect of high bias sparse feature

The hypothesis that a highly biased and sparsely populated feature could be mitigated with boosted weak learners is something I wanted to test. The re-introduction of the loan advance data should be validated. For the first attempt at this validation, I took the stock adaboost algorithm and trained it on 100 random data splits. Each split was seeded with a value from 0-99. The statisics from these runs suggest inclusion of this feature is negligible on the performance of the learner.

```{Python}
With Loan Data: DescribeResult(nobs=100L, minmax=(0.5333333333333333, 1.0), mean=0.8600000000000001, variance=0.006778900112233446, skewness=-0.8439686930037359, kurtosis=1.8782509539055363)
Without Loan Data: DescribeResult(nobs=100L, minmax=(0.5333333333333333, 1.0), mean=0.8593333333333334, variance=0.006904152637485971, skewness=-0.8290566801887221, kurtosis=1.7280531992655
```

After increasing the number of estimators, There was no change in the value of the sparsely populated features towards classification.

```{python}
[('salary', 0.077),
 ('deferral_payments', 0.0154),
 ('total_payments', 0.0994),
 ('bonus', 0.0448),
 ('restricted_stock_deferred', 0.0002),
 ('deferred_income', 0.0566),
 ('total_stock_value', 0.12),
 ('expenses', 0.1792),
 ('loan_advances', 0.0),
 ('exercised_stock_options', 0.105),
 ('other', 0.1644),
 ('long_term_incentive', 0.0516),
 ('restricted_stock', 0.0864),
 ('director_fees', 0.0)]
5000 estimator accuracy score: 0.733333333333
```

Going higher on the number of estimators still give accuracy within the wide range of values and no still weight to the sparsely populated features.  

```{python}
[('salary', 0.044606),
 ('deferral_payments', 0.010066),
 ('total_payments', 0.096564),
 ('bonus', 0.036498),
 ('restricted_stock_deferred', 0.002396),
 ('deferred_income', 0.074054),
 ('total_stock_value', 0.140456),
 ('expenses', 0.087702),
 ('loan_advances', 0.0),
 ('exercised_stock_options', 0.131746),
 ('other', 0.114154),
 ('long_term_incentive', 0.053164),
 ('restricted_stock', 0.208594),
 ('director_fees', 0.0)]
500000 estimator accuracy: 0.6
```

How the data is split appears to have a great effect on the training of our classifier. It also probably doesn't help that we have additional features that just aren't useful to the model. The assumption that went into using an adaboost classifier trained on sparse data do not appear to have panned out. It's not a total loss. A model of nuanced booleans may make for an interesting future case study. Plus in almost all classifiers, stock data was always highly weighted. This gives a clue that investigating how the stock game was played would provide a better case for this project's scope.  

## Stock Data

![Stock_data_pairplot](./pickle_jar/stock_pairplot.png)

A few things stick out in the relationships between the stock features.  
First, restricted_stock_deferred is a feature observed in only 12% of our population. It's quite sparse. If we were to ignore it we would be left with  two main stock features: exercised_stock and restricted_stock. It would be quite easy to and well within scope to ignore it but that would complicate the total_stock_value feature. Total_stock_value is a calculated feature. It could just be recalculated. Best thing to do is to recontextualize the values.

exercised_stock_options is the net value of the stock over the exercise price.  
restricted_stock is the gross value of restricted stock that lapsed in their vesting period.  
restricted_stock_deferred appears to be where the lapsed restricted_stock was placed into the deferred income plan rather than liquidated.  

So restricted_stock_deferred should always be negative as it subtracts from restricted_stock. Why then is there an entry with positive restricted_stock_deferred?  

```{python}
     restricted_stock_deferred  total_stock_value  exercised_stock_options  restricted_stock
103                 15456290.0                0.0                2604490.0        -2604490.0
BHATNAGAR SANJAY has positive restricted stock deferrals
{'bonus': 'NaN',
 'deferral_payments': 'NaN',
 'deferred_income': 'NaN',
 'director_fees': 137864,
 'email_address': 'sanjay.bhatnagar@enron.com',
 'exercised_stock_options': 2604490,
 'expenses': 'NaN',
 'from_messages': 29,
 'from_poi_to_this_person': 0,
 'from_this_person_to_poi': 1,
 'has_email_statistics': True,
 'has_financial': True,
 'loan_advances': 'NaN',
 'long_term_incentive': 'NaN',
 'other': 137864,
 'poi': False,
 'restricted_stock': -2604490,
 'restricted_stock_deferred': 15456290,
 'salary': 'NaN',
 'shared_receipt_with_poi': 463,
 'to_messages': 523,
 'total_payments': 15456290,
 'total_stock_value': 'NaN'}

```

Seems this data is dirtier than we first assumed. As we've reduced the scope of our classifier to just the stock data, it shouldn't be too difficult to add in some validators to the data cleaner. Just to catch anyone else with oddly shifted data.

```{Python}
BELFER ROBERT does not have sane stock totals.
poi = False
restricted_stock_deferred = 44093
total_stock_value = -44093
exercised_stock_options = 3285
restricted_stock = NaN

BHATNAGAR SANJAY does not have sane stock totals.
poi = False
restricted_stock_deferred = 15456290
total_stock_value = NaN
exercised_stock_options = 2604490
restricted_stock = -2604490
```

Seems Sanjay isn't the only person with poorly parsed stock data. While it would be best to correct the error in the data wrangler, that is out of scope for this project. Instead, I'll just drop these non-poi from the dataset.  

![stock_pairplot_cleaned](./pickle_jar/stock_pairplot_cleaned.png)

Now the data is seeming sane. Deferred restricted stock is on a negative scale, and there's no negative values for restricted stock. Exercised stock options and total stock appear highly correlated. That makes sense as total stock value is a calculated value and exercised stock is only additive. That leaves the stock dataset as observations of 3 features.  

![stock_pairplot_sans_redundant](./pickle_jar/stock_pairplot_sans_redundant.png)

This is a much more managable set of features. However, I do have some consern of how narrow it is. Looking back at investigation of the full financial data, there's one feature that should be re-included. Specifically the total payments field from the other part of the financial data set. Like the stock data, it has an acceptable level of observations and was consistently weighed highly with the adaboost classifiers. It offers information at the low cost of a single dimension. Checking for the sanity of the total payment field returns only those two people we've already flagged for removal for non-sane total stock values.

```{Python}
BELFER ROBERT does not have sane payment totals.
poi = False
salary = NaN
deferral_payments = -102500
total_payments = 102500
bonus = NaN
deferred_income = NaN
expenses = NaN
loan_advances = NaN
other = NaN
long_term_incentive = NaN
director_fees = 3285

BHATNAGAR SANJAY does not have sane payment totals.
poi = False
salary = NaN
deferral_payments = NaN
total_payments = 15456290
bonus = NaN
deferred_income = NaN
expenses = NaN
loan_advances = NaN
other = 137864
long_term_incentive = NaN
director_fees = 137864
```

If we are re-introducing total_payments as the informational portion of the payment data, we would be remiss if we did not also include the deferred income component. Much like restricted_stock_deferred is the negative to total stocks, it is the negative component to total pay.

![./pickle_jar/fin_data_pairplot.png](./pickle_jar/fin_data_pairplot.png)

## Feature Selection Validation

To this point, feature selection has been a manual process resulting from a familirization with the data due to data investigation. As much as I'd like to believe my instincts and eyeballs are good, I do not believe that's good enough for data science. So I'd like to take a small detour and validate my unorthodox use of adaboost to identify features by a more accepted means of feature selection.

```{Python}
[('deferred_income', -1.3650468360827975e-07),
 ('deferral_payments', -8.141966143698239e-08),
 ('other', -6.108570287861131e-08),
 ('director_fees', -5.794583665478616e-08),
 ('long_term_incentive', -1.1534852970185745e-08),
 ('loan_advances', -5.4387922244909575e-09),
 ('restricted_stock_deferred', -4.407784434320726e-09),
 ('restricted_stock', -2.997067712758703e-09),
 ('total_stock_value', 6.456635773571899e-09),
 ('total_payments', 7.046569603493372e-09),
 ('exercised_stock_options', 7.610473458563938e-09),
 ('bonus', 2.8047104220078648e-08),
 ('expenses', 3.9816279164494394e-07),
 ('salary', 4.077777256337691e-07)]
```

Performing a rough Lasso regression to determine the most impactful financial features mostly agrees with my estimates. What I missed are salary, expenses and bonus. Each of these are weighted higher for classification than the stock features even though they have less population in the observations. Given their relation to total_payments, I was correct to re-introduce total_payments to my feature selection. Given these weights, including deferred_income is very questionable.  

With this new information at hand, I'll once again shift direction on what information to feed my classifier. The redundant information of total_payments and total_stock_value will be removed. Features weighed in the negative will also be removed. That leaves bonus, expenses and salary as granular components of total_pay end exercised_stock_options as the principal component of total_stock_value. It's basically the same data model as I had already decided on except now flipping which set is more granular.  

![./pickle_jar/data_pairplot.png](./pickle_jar/data_pairplot.png)  

Definitely a more interesting set of plots.  

## Data Scaling

Even though the plots of this final dataset are more interesting, I question how some seem compressed and there's some heteroskedasticity. It would be best to apply some preprocessing.

![./pickle_jar/preped_data_pairplot.png](./pickle_jar/preped_data_pairplot.png)

Scaling the data to unit variance has done nothing for the dispersion of points. It does open us up to classifiers that are dependant on similarly scaled data. The data should now be in a good place to compare the performance of some classifiers

## Classifier Tuning

Enough with the scope creep. Let's train and tune some classifiers

### Untuned, Stock Classifiers

To start with the classifiers proper, I trained a handful on their stock settings with a simple 90%/10% training/testing data split.

> Stock configuration K-NN mean accuracy: 0.875  
> Stock configuration SVM mean accuracy: 0.9  
> Stock configuration linear coefficient of determination: 0.191549987364  

Out of the box SVM appears to have the best prediction accuracy. K-NN isn't too far off. I just don't necessarily trust these numbers. When I was training an adaboost classifier on higher dimensional sparse data the accuracy was highly data dependent. It seemed to be overfitting the data. It would be good to verify that's not the case here.  

The score on the linear regression is quite poor. This isn't too surprising. Recalling the pair plots, that's not a big surprise. Ordinary least squares linear regression does poorly in data with a lot of heteroskedasticity. I'm going to drop it as an option for classifying this data.  

### Cross Validation

To get a better idea on the accuracy of regardless of the data split some cross validation scores were obtained

```{python}
stock knn cross validation scores
[0.85714286 0.85714286 0.78571429 0.84615385 0.69230769 0.84615385
 0.84615385 0.76923077 0.91666667 0.91666667]
stock knn accuracy: 0.83 (+/- 0.13)
stock svm cross validation scores
[0.85714286 0.85714286 0.85714286 0.84615385 0.84615385 0.84615385
 0.84615385 0.84615385 0.91666667 0.91666667]
stock svm accuracy: 0.86 (+/- 0.05)
```

The deviation of K-Nearest Neighbors in our 10-fold cross validation is quite high and the accuracy is worse. Looks like SVM is our winner for tuning and final submission.  

### Tuning the SVM classifier

There's a few options for tuning the SVM classifier. Two of them appear critical.  

* C: Penalty parameter C of the error term. Quite literally more bias or variance. Will adjust this last.
* kernel: There's a few options here with rbf being the default.

Most of the rest of the tuning parameters are kernel specific.

```{python}
***SVM Kernal Testing***
[0.85714286 0.85714286 0.85714286 0.84615385 0.92307692 0.84615385
 0.84615385 0.92307692 0.91666667 0.91666667]
linear accuracy: 0.88 (+/- 0.07)
linear precision_score: 0.200
linear recall_score: 0.500

[0.85714286 0.92857143 0.85714286 0.76923077 0.84615385 0.84615385
 0.84615385 0.84615385 0.91666667 0.91666667]
poly accuracy: 0.86 (+/- 0.09)
poly precision_score: 0.286
poly recall_score: 0.500

[0.85714286 0.85714286 0.85714286 0.84615385 0.84615385 0.84615385
 0.84615385 0.84615385 0.91666667 0.91666667]
C:\ProgramData\Anaconda3\envs\py27\lib\site-packages\sklearn\metrics\classification.py:1143: UndefinedMetricWarning: Precision is ill-defined and being set to 0.0 due to no predicted samples.
  'precision', 'predicted', average, warn_for)
rbf accuracy: 0.86 (+/- 0.05)
rbf precision_score: 0.000
rbf recall_score: 0.000

[0.85714286 0.92857143 0.85714286 0.84615385 0.84615385 0.84615385
 0.84615385 0.84615385 0.75       0.91666667]
sigmoid accuracy: 0.85 (+/- 0.09)
sigmoid precision_score: 0.286
sigmoid recall_score: 0.500
```

The stock rbf kernal is throwing an error for no predicted samples. After investigating this error, it's correct. The rbg kernal is not predicting anyone. Looking at our data set, 86% accuracy is inline with a classifier that classifies nothing.  

## Metrics

Some revisting on the topic of metrics.  

Basic accuracy is the number of correctly classified items. When using this as a metric, it's important to remember the statistics of blind guessing. This is what was encountered with the SVM classifier. Accuracy has no concern about what the classification was, only that the classification was correct. Precision and recall measure the relevance of a specific label.  

* Accuracy tells how many ducks and how many geese were correctly labeled as a duck or goose. How many 'true duck and true geese' out of all 'ducks and geese'
* Recall states how many of the ducks were identified as ducks. Every duck labeled as a goose causes recall to decrease.
  * How many 'true ducks' out of all 'true ducks and false geese'
  * Ratio of 'duck is duck' out of all 'duck is duck' and 'goose is duck'.
* Precision states how many identified ducks are actually ducks. Every goose labeled as a duck causes precision to decrease.
  * How many 'true ducks' out of all 'true ducks and false ducks'.
  * Ratio of 'duck is duck' for all 'duck is duck' and 'duck is goose'.

For our poi identifier, accuracy doesn't tell us if we correctly classified a person of interest. It tells us the probability a person was correctly classified. Instead, we need to look at precision and recall. Recall describes how many poi we missed. Precision describes how many innocents were caught in our poi sweep. The F1-Score is a combination of these values. The selection process of the classifier needs revisitng. Precision and recall are more relevant to our use case than accuracy.  

Given the project requirement of at least 30% precision, that will be our metric

```{python}
"Support Vector Classifier's best precision is: 0.305"
'K-Nearest Neighbors best precision is: 0.226'
GridSearchCV(cv=10, error_score='raise-deprecating',
       estimator=Pipeline(memory=None,
     steps=[('standardscaler', StandardScaler(copy=True, with_mean=True, with_std=True)), ('svc', SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0,
  decision_function_shape='ovr', degree=3, gamma='scale', kernel='rbf',
  max_iter=-1, probability=False, random_state=None, shrinking=True,
  tol=0.001, verbose=False))]),
       fit_params=None, iid='warn', n_jobs=None,
       param_grid={'svc__kernel': ('linear', 'rbf', 'sigmoid', 'poly'), 'svc__C': [1, 2, 3, 4, 5, 6, 7, 8, 9]},
       pre_dispatch='2*n_jobs', refit=True, return_train_score='warn',
       scoring=make_scorer(precision_score), verbose=0)
```

## Redo

At this point, we're on to submission. Check Project_QnA.md and ReviewRefinements for more brain dumps.  

## Research sources

### Articles on 409A and Deferred Payments

[https://executivebenefitsolutions.com/lessons-learned-from-enron-and-chrysler-how-to-secure-nonqualified-deferred-compensation-plans/](https://executivebenefitsolutions.com/lessons-learned-from-enron-and-chrysler-how-to-secure-nonqualified-deferred-compensation-plans/)  
[https://www.institutionalinvestor.com/article/b150nnb56pj7fj/blame-it-on-enron](https://www.institutionalinvestor.com/article/b150nnb56pj7fj/blame-it-on-enron)  

### Who is Eugene Lockhart and the New Power Company

[https://money.cnn.com/2000/05/16/technology/enron/](https://money.cnn.com/2000/05/16/technology/enron/)  
[https://www.wsj.com/articles/SB1017015132933556040](https://www.wsj.com/articles/SB1017015132933556040)  

### Preventing Bias

[https://towardsdatascience.com/preventing-machine-learning-bias-d01adfe9f1fa](https://towardsdatascience.com/preventing-machine-learning-bias-d01adfe9f1fa)  
[https://qz.com/1585645/color-blindness-is-a-bad-approach-to-solving-bias-in-algorithms/](https://qz.com/1585645/color-blindness-is-a-bad-approach-to-solving-bias-in-algorithms/)  

### PPCA

[http://edwardlib.org/tutorials/probabilistic-pca](http://edwardlib.org/tutorials/probabilistic-pca)  
[http://www.miketipping.com/papers/met-mppca.pdf](http://www.miketipping.com/papers/met-mppca.pdf)

### Adaboost

[https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.AdaBoostClassifier.html](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.AdaBoostClassifier.html)

### Regularization and Preprocessing

[Statquest Part 1: Ridge Regression](https://www.youtube.com/watch?v=Q81RR3yKn30)
[Statquest Part 2: LASSO Regression](https://www.youtube.com/watch?v=NGf0voTMlcs)

[https://scikit-learn.org/stable/modules/preprocessing.html#preprocessing-scaler](https://scikit-learn.org/stable/modules/preprocessing.html#preprocessing-scaler)  

### Feature and Algorithm selection

[https://scikit-learn.org/stable/tutorial/machine_learning_map/index.html](https://scikit-learn.org/stable/tutorial/machine_learning_map/index.html)  
[https://www.quora.com/How-do-I-properly-use-SelectKBest-GridSearchCV-and-cross-validation-in-the-sklearn-package-together](https://www.quora.com/How-do-I-properly-use-SelectKBest-GridSearchCV-and-cross-validation-in-the-sklearn-package-together)  

## Questions

1. Summarize for us the goal of this project and how machine learning is useful in trying to accomplish it. As part of your answer, give some background on the dataset and how it can be used to answer the project question. Were there any outliers in the data when you got it, and how did you handle those?  [relevant rubric items: “data exploration”, “outlier investigation”]

1. What features did you end up using in your POI identifier, and what selection process did you use to pick them? Did you have to do any scaling? Why or why not? As part of the assignment, you should attempt to engineer your own feature that does not come ready-made in the dataset -- explain what feature you tried to make, and the rationale behind it. (You do not necessarily have to use it in the final analysis, only engineer and test it.) In your feature selection step, if you used an algorithm like a decision tree, please also give the feature importances of the features that you use, and if you used an automated feature selection function like SelectKBest, please report the feature scores and reasons for your choice of parameter values.  [relevant rubric items: “create new features”, “intelligently select features”, “properly scale features”]

1. What algorithm did you end up using? What other one(s) did you try? How did model performance differ between algorithms?  [relevant rubric item: “pick an algorithm”]

1. What does it mean to tune the parameters of an algorithm, and what can happen if you don’t do this well?  How did you tune the parameters of your particular algorithm? What parameters did you tune? (Some algorithms do not have parameters that you need to tune -- if this is the case for the one you picked, identify and briefly explain how you would have done it for the model that was not your final choice or a different model that does utilize parameter tuning, e.g. a decision tree classifier).  [relevant rubric items: “discuss parameter tuning”, “tune the algorithm”]

1. What is validation, and what’s a classic mistake you can make if you do it wrong? How did you validate your analysis?  [relevant rubric items: “discuss validation”, “validation strategy”]

1. Give at least 2 evaluation metrics and your average performance for each of them.  Explain an interpretation of your metrics that says something human-understandable about your algorithm’s performance. [relevant rubric item: “usage of evaluation metrics”]
