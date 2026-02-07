## DSE Stock Price Prediction using Hidden Markov Model

Raihan Tanvir GLYPH&lt;6&gt; § , Md Tanvir Rouf Shawon GLYPH&lt;6&gt; § , Md. Golam Rabiul Alam :

GLYPH&lt;6&gt; Ahsanullah University of Science and Technology, Dhaka, Bangladesh

: Brac University, Dhaka, Bangladesh

{ raihantanvir.96, shawontanvir95 } @gmail.com, rabiul.alam@bracu.ac.bd

Abstract -Stock market forecasting is a classic problem that has been thoroughly investigated using machine learning and artificial neural network based tools and techniques. Interesting aspects of this problem include its time reliance as well as its volatility and other complex relationships. To combine them, hidden markov models (HMMs) have been utilized to anticipate the price of stocks. We demonstrated the Maximum A Posteriori (MAP) HMM method for predicting stock prices for the next day based on previous data. An HMM is trained by analyzing the fractional change in the stock price as well as the intraday high and low values. It is then utilized to produce a MAP estimate across all possible stock prices for the next day. The approach demonstrated in our work is quite generalized and can be used to predict the stock price for any company, given that the HMM is trained on the dataset of that company's stocks dataset. We evaluated the accuracy of our models using some extensively used accuracy metrics for regression problems and came up with a satisfactory outcome.

Index Terms -Hidden Markov Models, Stock Price Forecasting, Time Series Analysis, Price Prediction.

## I. INTRODUCTION

Stock price forecasting has been one of the most difficult issues for the AI community. Typical AI research, which is primarily focused on building intelligent solutions that are meant to imitate human intelligence, has typically gone beyond the limits of forecasting research. Stock price forecasting, however, remains severely constrained because of its nonstationary, cyclic, and stochastic character. A variety of factors influence the rate of price fluctuations in such a series, including equity, the rate of interest, options, securities, warrants, mergers and acquisitions of significant financial organizations, and so on. In such market, ordinary investors can not profit regularly. As a result, an intelligent forecasting model for the stock market would be highly demanded and of significant interest to ordinary investors.

HMMs are seen as successful in analyzing and forecasting time-dependent events. This technique has already been used for voice recognition [1], handwriting recognition [2], facial expression recognition [3], ECG analysis [4], and other purposes. Stock market forecasting is analogous to these problems in terms of its inherent relationship with time. Based on an unseen collection of states from which transitions can be made, hidden Markov models correlate each state with a probable observation. In a similar fashion, the stock market can be

§ Authors have equal contribution

seen. Investors are usually unaware of the inherent factors that influence share prices. Transitions between these underlying states are influenced by business strategy, decisions, the market environment, etc. The stock's value is the observable result that reflects these. So, HMM obviously complies with this real-world setting.

The selection of features is very crucial in this method. Several attempts have been made in the past to use the volume of trade, the stock's momentum, as well as the market's correlation and volatility. We incorporate the daily fractional differences in stock values as well as the fractional deviation of intraday maximum and minimum values, as proposed in [5]. It is essential to comprehend the fractional change to generate the desired prediction. The fractional difference between the intraday high and low values is a good predictor of volatility direction.

Despite the fact that HMMs have been utilized in this area for a long time, none of the works have contributed to the Bangladesh stock market. As a response, we opted to use a HMM-based approach to serve this purpose. To employ the technique, we use stock data from companies listed on the Dhaka Stock Exchange (DSE). For each stock, a unique HMM is trained. The sole constraint that the training dataset must satisfy is significant variability in the observations. It is resolved by effectively using long spans of time (13 years) during which the stock price swings consistently, albeit significantly.

## II. PREVIOUS WORKS

Various studies have been conducted recently in an attempt to develop a stock market forecasting model that is flawless (or close so). In most of the forecasting research, statistical time series analysis methodologies such as the auto-regression moving average (ARMA) [6] and multiple regression approaches are utilized.

A HMM based approach for stock price forecasting [5] is deeply studied. For predicting the following day´ s stock value given historical data, the authors followed the Maximum a Posteriori HMM method. The continuous HMM is trained using the fractional difference in stock values and the stock's intraday highs and lows. After much deliberation, we decided to use the technique outlined in this paper to develop our model.

Fig. 1. Hidden Markov Model

<!-- image -->

In [7], a directed-weighted chunking SVMs approach is described, where the complete training dataset is partitioned into numerous sections and support vectors for each portion are created. To create the forecast model, weighted support vector regressions are computed on the new working data set.

Md. Rafiul Hassan et al. introduced [8], an HMM-based model in which predictions are generated by interpolating the adjacent values of the dataset. The results achieved from this experiment are inspiring, and a novel framework for stock market analysis is explored.

Using autonomously generated fuzzy connections, Romahi Y et al. introduced a unique technique to dynamic financial forecasting [9]. This method has yielded promising results, but building a fuzzy system requires domain expertise.

H. Liu et al. offered a deep residual network based strategy for prediction where the stock price graph is utilized as an input [10]. This model's average accuracy was 0 . 40 , which is higher than the stochastic indicator's average accuracy of 0 . 33 .

Also, a naive approach demonstrated in the official documentation of the hmmlearn package is thoroughly investigated. In this scheme, only the difference between two consecutive closing prices of a stock is considered. Though it's a simple approach and ignores several key factors in stock price prediction, it has shown quite satisfactory results.

## III. METHODOLOGY

An HMM, λ may be represented as,

λ GLYPH&lt;16&gt; p π, A, B q , where A is the transition matrix, the entries of which represent the likelihood of a state switching from one state to another, B is the emission matrix, that provides b j p O t q the probability of witnessing O t while in state j and, π represents the initial probabilities of the states at time, t GLYPH&lt;16&gt; 1 . We consider the emission probability distribution to be continuous, since the samples are a vector of continuous random variables. For simplicity, we'll consider it a multinomial Gaussian distribution having parameters, ( µ and Σ )

The model's observation is a three dimensional vector representing daily stock information,

<!-- formula-not-decoded -->

In (1) open represents the day's opening price, close denotes the day's closing price, high and low represent the day's highest price and lowest price, respectively. To characterize the variance in stock values that stays constant throughout time, we utilize fractional changes.

After training, an approximation of the Maximum a Posteriori (MAP) technique is employed to test it. When projecting future stock prices, we assume a d day latency. As a result, having the HMM model, λ and the stock prices for previous d days p O 1 , O 2 , . . . , O d q , as well as the opening price for the p d GLYPH&lt;0&gt; 1 q st day, the task is to calculate the closing price for the p d GLYPH&lt;0&gt; 1 q st day, which is equivalent to computing the fractional difference for the p d GLYPH&lt;0&gt; 1 q st day, close GLYPH&lt;1&gt; open open . This is done using the MAP approximation of the observation vector, O d GLYPH&lt;0&gt; 1 .

Lets consider ˆ O d GLYPH&lt;0&gt; 1 , the MAP value of the observation on the d GLYPH&lt;0&gt; 1 day, provided the values of the previous d days.

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

The observation vector p O d GLYPH&lt;0&gt; 1 q is adjusted throughout the whole range of potential values. Because the denominator is invariant with regard to p O d GLYPH&lt;0&gt; 1 q the MAP approximation reduces to (4).

<!-- formula-not-decoded -->

We determine the maximum probability by computing the probability across a distinct set of potential O d GLYPH&lt;0&gt; 1 values. The computational cost of determining the likelihood of a particular observation is O p n 2 d q , where n denotes the number of states and d denotes the latency. This process is repeated for all distinct set of potential values of O d GLYPH&lt;0&gt; 1 . We have n GLYPH&lt;16&gt; 4 , d GLYPH&lt;16&gt; 30 and the number of possible values of O d GLYPH&lt;0&gt; 1 is 50 GLYPH&lt;2&gt; 10 GLYPH&lt;2&gt; 10 (see table II). The closing price of a given day can be determined by taking the day's opening price and incorporating it with the expected fractional difference for that day as shown in (5).

<!-- formula-not-decoded -->

We also employed a naive approach, where only the differences in the closing prices of two successive days of stock are considered. The observations in this approach are the difference in closing prices for two consecutive days and the volume of stocks. After training the model, a prediction is made by computing the inner product of the transition matrix and the mean of the observations. Finally, the predicted changes are incorporated with the previous day's closing price to generate the ultimate prediction.

## IV. DATASET

To put the chosen technique into practice, we selected the DSEBD 1 dataset from Kaggle. The dataset consists of annual stock data of companies registered to Dhaka Stock Exchange

Fig. 2. Predicting Closing Price Using Fractional Changes

<!-- image -->

Fig. 3. Trend of opening, closing, highest and lowest prices for ACI stocks (100 samples)

<!-- image -->

(DSE) from January 2008 to December 2020 in separate JSON files. The dataset contains stock records for a total of 589 companies from 22 different sectors with 5 unique instrument types. The number of observations in the dataset is 15 , 75 , 134 .

To fit the dataset into our scheme, the following steps of processing have been performed.

- GLYPH&lt;13&gt; The json files are loaded into pandas data-frame and stored into a list of data-frames
- GLYPH&lt;13&gt; The items of the list are concatenated into a single dataframe
- GLYPH&lt;13&gt; The concatenated frame is saved as csv.
- GLYPH&lt;13&gt; Separate Dataset is created by extracting the data for individual stocks from the concatenated frame.

The dataset is split into 0 . 8 : 0 . 2 ratio using train test split function supplied by sklearn.model selection module, where 80% data is used in train set and rest of the 20% is used for test set. As we are working with time-series data, we need to preserve the temporal sequence of the data. To avoid

Fig. 4. Trend of closing prices for ACI's Stocks from Jan 2008 to Dec 2020.

<!-- image -->

TABLE I SAMPLE DATA FROM ACI STOCKS DATASET

| date       |   open |   high |   low |   close |   volume |   prev close |
|------------|--------|--------|-------|---------|----------|--------------|
| 2008-03-06 |  200   |  202   | 194   |   195.5 |   266850 |        198.8 |
| 2008-03-09 |  199.8 |  199.8 | 194   |   195   |   333600 |        195.5 |
| 2008-03-09 |  199.8 |  199.8 | 194   |   195   |   333600 |        195.5 |
| 2008-03-10 |  196.5 |  209.5 | 195.4 |   207.3 |   381650 |        195   |
| 2008-03-11 |  209.9 |  217.9 | 207   |   215.5 |   509550 |        207.3 |

random splitting of data into train and test sets, we passed shuffle=False as the parameter.

The trend of the stock price of ACI Limited is shown in the figure 3 and 4. Table I shows some sample data from ACI stocks dataset.

## V. IMPLEMENTATION

As our HMM, we employed the GaussianHMM class from the hmmlearn 2 package and performed parameter approximation using the fit method provided by it. Because we investigated two approaches, we'll go through the implementation specifics of the first technique, which uses fractional changes in stock prices. Following that, the execution of a later strategy that takes into account successive price fluctuations in stocks is addressed.

## A. HMM with Fractional Changes

- 1) Initialization:: The initialization of the HMM is done by setting the parameters according to following configurations:
2. GLYPH&lt;13&gt; Quantity of hidden states, n = 4
3. GLYPH&lt;13&gt; Dimension of observations, D = 3
4. GLYPH&lt;13&gt; Latency, d = 30 days
5. GLYPH&lt;13&gt; Max number of iterations, n iter GLYPH&lt;16&gt; 10000
6. GLYPH&lt;13&gt; Convergence threshold tol GLYPH&lt;16&gt; 0 . 001

These values are obtained from [5], on the basis of which we're developing our model. Furthermore, [11] recommended using 4 underlying states because the dimension of observation is likewise 4 . The remaining model parameters are initialized with the default values of the GaussianHMM class provided by the hmmlearn package.

2 https://hmmlearn.readthedocs.io/en/latest/

Fig. 5. Correlation matrix for ACI stocks data

<!-- image -->

- 2) Training:: Though our dataset has many features, not all of them have a strong influence on the closing price of a stock. From the correlation matrix in figure 5, we can see that the opening price, highest price, and lowest price have a strongly positive relationship with the closing price (exactly 1 or very close to 1). Hence, we consider these four features to be the attributes of our interest.

Now, we have relatively few characteristics for each day, primarily the starting and ending prices of the stock for that day, as well as the maximum and minimum prices of the stock. So, we utilize them to compute stock prices. Instead of directly using these values, we extracted the fractional differences in each of them that would be used to train our HMM.

Following feature extraction, some rows may include NaN, infinity, or values that are too big for dtype('float64'). A data cleansing procedure is carried out to remove such data. After performing the aforementioned two operations, the HMM is trained using the fit method of GaussianHMM class with the obtained feature vectors. Though the n iter , was set 10000 , yet the training was early stopped after 35 iterations, due to the convergence threshold, tol .

- 3) Prediction:: Once our model has been trained, we then estimate the stock's closing price. Provided the opening stock price for a day and the data from the previous d days, we may compute the closing stock price for that day. Our predictor would have a latency of d day. This means that if we can estimate frac change for a particular day, we can calculate the closing price using the (5).

The optimization of the problem would have been computationally expensive if frac change is considered as a continuous variable. As a result, we discretized them into values within the boundaries of two finite variables (as shown in the table II) and generated a set of fractional changes, GLYPH&lt;160&gt; frac change , f rac high , f rac low ¡ by deriving the cartesian products of these three variables. A higher number of steps is used for the frac change since these are eventually utilized for

TABLE II RANGE OF VALUES FOR DIVIDING FRACTIONAL CHANGES

| Observation   |   Min Value |   Max Value |   Number of Steps |
|---------------|-------------|-------------|-------------------|
| frac change   |        -0.1 |         0.1 |                50 |
| frac high     |         0   |         0.1 |                10 |
| frac low      |         0   |         0.1 |                10 |

stock prediction. Then, the log probability under the model for the observation sets from the previous d days are derived using the score method of the GaussianHMM class, and the maximum is found. This way, the most probable outcome i.e: frac change is found and the closing price is computed using Equation 5. For predicting d days stock price, this method is called iteratively for those days index. Figure 6 and 7 shows the actual stock price along with the forecasted price using our trained model for ACI Limited and Grameenphone Limited respectively. The method we are following is a generalized approach and can be used to build a predictor for any company given that the HMM is trained on the dataset of that company's stock. Hence, we could use the same approach and build a separate prediction model for each of the companies listed on the Dhaka Stock Exchange.

## B. HMM with Successive Fluctuations

We followed the same settings for initialization in this method as in the previously described approach. The difference is in the feature set considered for this technique.

Fig. 8. The fluctuations in closing prices for ACI stocks.

<!-- image -->

- 1) Training:: To train the model with this approach, we first extracted the closing prices and volumes of the stocks. Then the successive difference between stock prices is calculated and stored. Finally, the tuple of dates, consecutive differences, and volumes is stacked vertically to form the feature vectors. Finally, the model is trained with these feature vectors. It took 240 iterations for the convergence of the model.
- 2) Prediction:: Since our model is trained to detect the pattern of changes in the closing price, it is ready to make a prediction of the changes that would appear in the closing price of the next day, given the closing price of the previous day. To achieve this objective, the dot product of the transition matrix A and the mean of the data distribution are computed. Then we incorporated the value of the expected change with the value

Fig. 6. Actual v/s Forecasted Value for ACI stocks from Dec 02, 2020 to Dec 30, 2020 by HMM with Fractional Changes.

<!-- image -->

Fig. 7. Actual v/s Forecasted Value for GrameenPhone stocks from Dec 02, 2020 to Dec 30, 2020 by HMM with Fractional Changes.

<!-- image -->

of the previous closing price to make our final predictions on the closing price of that day. Figure 9 illustrates the ACI Limited's actual stock price along with the predicted price.

## C. Evaluation

To assess the performance of our models, three widely accepted performance metrics for regression task have been used.

Mean Absolute Error (MAE) is a straightforward measure that computes the absolute difference between actual and projected values. It is the most robust metric for outliers.

Root Mean Squared Error (RMSE) is self-explanatory; it is the square root of the mean squared error(MSE). MSE is the mean of squared difference between the true and predicted values.

Mean Absolute Percentage Error (MAPE) is the mean absolute error between the true and forecasted values in percentage.

<!-- formula-not-decoded -->

TABLE III EVALUATION OF PREDICTIONS MADE ON ACI STOCKS

| Metric   |   HMM frac change |   HMM succ fluctuation |
|----------|-------------------|------------------------|
| MAE      |            2.5064 |                 3.3382 |
| RMSE     |            3.4003 |                 5.8141 |
| MAPE     |            1.0265 |                 1.3672 |

here y i and p i is the true and forecasted values respectively and n is the number of days for which the data are evaluated.

Table III shows the metric scores for the ACI Limited´ s stocks using our trained model. Here we can see that, the MAPE values for the models' are 1 . 0265 and 1 . 3672 . A MAPE score of less than 5 indicates that the forecast's accuracy is acceptable, according to [12]. So we can conclude that our predictors' performance is quite excellent, leaving the limitations described in the later section aside.

## VI. LIMITATIONS AND FUTURE WORKS

We have considered a dataset that contains stock data from January 2008 to December 2020. There are many open-source

Fig. 9. Actual v/s Forecasted Value for ACI Ltd 's from Dec 02, 2020 to Dec 30, 2020 by HMM with Successive Fluctuations.

<!-- image -->

scrapping tools that facilitate the retrieval of the upto date stock information. Due to time constraints, we could not employ them. The stock market has a volatile property, and the prices of stocks may fluctuate to a large extent. For this type of scenario, our models fail to provide accurate predictions. We are willing to overcome this limitation by using various smoothing techniques in the future.

## VII. CONCLUSION

Artificial intelligence and machine learning techniques have been frequently used to forecast stock values in Bangladesh's stock market. To the best of our knowledge, none of them have yet exploited the efficiency of hidden markov models in their work. In our paper, we have demonstrated the capability of HMMs to predict stock prices using historical data. Two approaches have been investigated. And both of them provide satisfactory outcomes for typical cases. If we can gather more domain knowledge and apply techniques for handling the abrupt changes in stocks' values, then we may be able to achieve perfection in the accuracy of our model. Finally, we believe that our work will extend the window of research on forecasting using the Hidden Markov Model.

## REFERENCES

- [1] N. Najkar, F. Razzazi, and H. Sameti, 'A novel approach to hmmbased speech recognition system using particle swarm optimization,' 2009 Fourth International on Conference on Bio-Inspired Computing , pp. 1-6, 2009.
- [2] P. Kumawat, A. Khatri, and B. Nagaria, 'Comparative analysis of offline handwriting recognition using invariant moments with hmm and combined svm-hmm classifier.'
- [3] X. Jiang, 'A facial expression recognition model based on hmm,' in Proceedings of 2011 International Conference on Electronic and Mechanical Engineering and Information Technology , vol. 6, 2011, pp. 3054-3057.
- [4] R. Andreao, B. Dorizzi, and J. Boudy, 'Ecg signal analysis through hidden markov models,' IEEE Transactions on Biomedical Engineering , vol. 53, no. 8, pp. 1541-1549, 2006.
- [5] A. Gupta and B. Dhingra, 'Stock market prediction using hidden markov models,' in 2012 Students Conference on Engineering and Systems , 2012, pp. 1-4.
- [6] T. Kimoto, K. Asakawa, M. Yoda, and M. Takeoka, 'Stock market prediction system with modular neural networks,' in 1990 IJCNN International Joint Conference on Neural Networks , 1990, pp. 1-6 vol.1.
- [7] L. Cao and F. Tay, 'Financial forecasting using support vector machines,' Neural Computing and Applications , vol. 10, pp. 184-192, 05 2001.
- [8] M. Hassan and B. Nath, 'Stock market forecasting using hidden markov model: a new approach,' in 5th International Conference on Intelligent Systems Design and Applications (ISDA'05) , 2005, pp. 192-196.
- [9] Y. Romahi and Q. Shen, 'Dynamic financial forecasting with automatically induced fuzzy associations,' in Ninth IEEE International Conference on Fuzzy Systems. FUZZ- IEEE 2000 (Cat. No.00CH37063) , vol. 1, 2000, pp. 493-498 vol.1.
- [10] H. Liu and B. Song, 'Stock price trend prediction model based on deep residual network and stock price graph,' in 2018 11th International Symposium on Computational Intelligence and Design (ISCID) , vol. 02, 2018, pp. 328-331.
- [11] M. R. Hassan, 'A combination of hidden markov model and fuzzy model for stock market forecasting,' Neurocomputing , vol. 72, no. 16, pp. 3439-3446, 2009, financial Engineering Computational and Ambient Intelligence (IWANN 2007). [Online]. Available: https://www.sciencedirect.com/science/article/pii/S0925231209001805
- [12] D. A. Swanson, 'On the Relationship among Values of the Same Summary Measure of Error when it is used across Multiple Characteristics at the Same Point in Time: An Examination of MALPE and MAPE,' Review of Economics &amp; Finance , vol. 5, pp. 1-14, August 2015. [Online]. Available: https://ideas.repec.org/a/bap/journl/150301. html