#!/usr/bin/env python
# coding: utf-8

# # Generic Conditional Laws for Random-Fields - via:
# 
# ## Universal $\mathcal{P}_1(\mathbb{R})$-Deep Neural Model $\mathcal{NN}_{1_{\mathbb{R}^n},\mathcal{D}}^{\sigma:\star}$.
# 
# ---
# 
# By: [Anastasis Kratsios](https://people.math.ethz.ch/~kratsioa/) - 2021.
# 
# ---
# 
# ## What does this code do?
# 1. Learn Heteroskedastic Non-Linear Regression Problem
#      - $Y\sim f_{\text{unkown}}(x) + \epsilon$ where $f$ is an known function and $\epsilon\sim Laplace(0,\|x\|)$
# 2. Learn Random Bayesian Network's Law:
#     - $Y = W_J Y^{J-1}, \qquad Y^{j}\triangleq \sigma\bullet A^{j}Y^{j-1} + b^{j}, \qquad Y^0\triangleq x$
# 
# 3. In the above example if $A_j = M_j\odot \tilde{A_j}$ where $\tilde{A}_j$ is a deterministic matrix and $M_j$ is a "mask", that is, a random matrix with binary entries and $\odot$ is the Hadamard product then we recover the dropout framework.

# #### Mode:
# Software/Hardware Testing or Real-Deal?

# In[1]:


trial_run = True


# ### Simulation Method:

# In[2]:


# Random DNN
# f_unknown_mode = "Heteroskedastic_NonLinear_Regression"

# Random DNN internal noise
# f_unknown_mode = "DNN_with_Random_Weights"
Depth_Bayesian_DNN = 10
width = 20

# Random Dropout applied to trained DNN
f_unknown_mode = "DNN_with_Bayesian_Dropout"
Dropout_rate = 0.1

# Rough SDE (time 1)
f_unknown_mode = "Rough_SDE"


# #### Rough SDE Meta-Parameters

# In[3]:


# SDE with Rough Driver
N_Euler_Steps = 10**2
Hurst_Exponent = 0.001

def alpha(t,x):
    output_drift_update = t-x
    return output_drift_update

def beta(t,x):
    output_vol_update = (t+0.001)*np.diag(np.cos(x))
    return output_vol_update


# ---
# # Training Algorithm:
# ---
# - Random $\delta$-bounded partition on input space,
# - Train deep classifier on infered classes.
# ---
# ---
# ---
# ## Notes - Why the procedure is so computationally efficient?
# ---
#  - The sample barycenters do not require us to solve for any new Wasserstein-1 Barycenters; which is much more computationally costly,
#  - Our training procedure never back-propages through $\mathcal{W}_1$ since steps 2 and 3 are full-decoupled.  Therefore, training our deep classifier is (comparatively) cheap since it takes values in the standard $N$-simplex.
# 
# ---

# ## Load Auxiliaries

# In[4]:


# Load Packages/Modules
exec(open('Init_Dump.py').read())
# Load Hyper-parameter Grid
exec(open('CV_Grid.py').read())
# Load Helper Function(s)
exec(open('Helper_Functions.py').read())
# Import time separately
import time
os.environ['CUDA_VISIBLE_DEVICES'] = '0'


# load dataset
results_path = "./outputs/models/"
results_tables_path = "./outputs/results/"
raw_data_path_folder = "./inputs/raw/"
data_path_folder = "./inputs/data/"


### Set Seed
random.seed(2021)
np.random.seed(2021)
tf.random.set_seed(2021)


# ## Meta-Parameters

# ### Simulation

# ## Problem Dimension

# In[5]:


problem_dim = 10


# #### Grid Hyperparameter(s)
# - Ratio $\frac{\text{Testing Datasize}}{\text{Training Datasize}}$.
# - Number of Training Points to Generate

# In[6]:


train_test_ratio = .2
N_train_size = 10**2


# Monte-Carlo Paramters

# In[7]:


## Monte-Carlo
N_Monte_Carlo_Samples = 10**2


# Initial radis of $\delta$-bounded random partition of $\mathcal{X}$!

# In[8]:


# Hyper-parameters of Cover
delta = 0.01
Proportion_per_cluster = .5


# **Note**: Setting *N_Quantizers_to_parameterize* prevents any barycenters and sub-sampling.

# # Simulate from: $Y=f(X,W)$ 
# - Random DNN (internal noise): 
#     - $f(X,W) = f_{\text{unknown}}(X+U)$
# - Random DNN: 
#     - $f(X,W) = f_{\text{unknown}}(X)+W$
#     
# *Non-linear dependance on exhaugenous noise.*

# ## Heteroskedastic Regression Problem

# In[9]:


if f_unknown_mode == "Heteroskedastic_NonLinear_Regression":
    #-----------#
    # Build DNN #
    #-----------#
    W_feature = np.random.uniform(size=np.array([width,problem_dim]),low=-.5,high=.5)
    W_readout = np.random.uniform(size=np.array([1,width]),low=-.5,high=.5)
    # Generate Matrices
    for i_weights in range(Depth_Bayesian_DNN):
        W_hidden_loop = np.random.uniform(size=np.array([width,width]),low=-.5,high=.5)
        if i_weights == 0:
            W_hidden_list = [W_hidden_loop]
        else:
            W_hidden_list.append(W_hidden_loop)
    # Define DNN Applier
    def f_unknown(x):
        x_internal = x.reshape(-1,)
        x_internal = np.matmul(W_feature,x)
        #Deep Layer(s)
        for i in range(Depth_Bayesian_DNN):
            W_internal = W_hidden_list[i]
            x_internal = np.matmul(W_internal,x_internal)
            x_internal = np.maximum(0,x_internal)    
        # Readout Layer
        x_internal = np.matmul(W_readout,x_internal)
        return x_internal

    # Define Simulator
    def Simulator(x_in):
        var = np.sqrt(np.sum(x_in**2))
        # Pushforward
        f_x = f_unknown(x_in)
        # Apply Noise After
        noise = np.random.laplace(0,var,N_Monte_Carlo_Samples)
        f_x_noise = np.cos(f_x) + noise
        return f_x_noise


# ## Bayesian DNN

# In[10]:


if f_unknown_mode == "DNN_with_Random_Weights":
    def f_unknown(x):
        x_internal = x.reshape(-1,) 
        # Feature Map Layer
        W_feature = np.random.uniform(size=np.array([width,problem_dim]),low=-.5,high=.5)
        x_internal = np.matmul(W_feature,x)
    #     Deep Layer(s)
        for i in range(Depth_Bayesian_DNN):
            W_internal = np.random.uniform(size=np.array([width,width]),low=-.5,high=.5)
            x_internal = np.matmul(W_internal,x_internal)
            x_internal = np.maximum(0,x_internal)    
        # Readout Layer
        W_readout = np.random.uniform(size=np.array([1,width]),low=-.5,high=.5)
        x_internal = np.matmul(W_readout,x_internal)
        return x_internal


    def Simulator(x_in):
        for i_MC in range(N_Monte_Carlo_Samples):
            y_MC_loop = f_unknown(x_in)
            if i_MC == 0:
                y_MC = y_MC_loop
            else:
                y_MC = np.append(y_MC,y_MC_loop)
        return y_MC


# ## Bayesian Dropout

# In[11]:


if f_unknown_mode == "DNN_with_Bayesian_Dropout":
    # Initialize Drouput Parameters
    N_Dropout = int(np.maximum(1,round(width*Dropout_rate)))
    
    #-----------#
    # Build DNN #
    #-----------#
    W_feature = np.random.uniform(size=np.array([width,problem_dim]),low=-.5,high=.5)
    W_readout = np.random.uniform(size=np.array([1,width]),low=-.5,high=.5)
    # Generate Matrices
    for i_weights in range(Depth_Bayesian_DNN):
        W_hidden_loop = np.random.uniform(size=np.array([width,width]),low=-.5,high=.5)
        if i_weights == 0:
            W_hidden_list = [W_hidden_loop]
        else:
            W_hidden_list.append(W_hidden_loop)
    # Define DNN Applier
    def f_unknown(x):
        x_internal = x.reshape(-1,)
        x_internal = np.matmul(W_feature,x)
        #Deep Layer(s)
        for i in range(Depth_Bayesian_DNN):
            W_internal = W_hidden_list[i]
            # Apply Random Dropout
            random_mask_coordinates_i = np.random.choice(range(width),N_Dropout)
            random_mask_coordinates_j = np.random.choice(range(width),N_Dropout)
            W_internal[random_mask_coordinates_i,random_mask_coordinates_j] = 0
            # Apply Dropped-out layer
            x_internal = np.matmul(W_internal,x_internal)
            x_internal = np.maximum(0,x_internal)    
        # Readout Layer
        x_internal = np.matmul(W_readout,x_internal)
        return x_internal

    def Simulator(x_in):
        for i_MC in range(N_Monte_Carlo_Samples):
            y_MC_loop = f_unknown(x_in)
            if i_MC == 0:
                y_MC = y_MC_loop
            else:
                y_MC = np.append(y_MC,y_MC_loop)
        return y_MC


# ### fSDEs
# Lean the conditional law of $I_{X_1 \in Ball(0,1)}$ where $X_t$ solves an SDE with fBM driver.

# In[12]:


if f_unknown_mode == "Rough_SDE":
    # Initialize Drouput Parameters
    N_Dropout = int(np.maximum(1,round(width*Dropout_rate)))
    
    #-----------#
    # Build DNN #
    #-----------#
    W_feature = np.random.uniform(size=np.array([width,problem_dim]),low=-.5,high=.5)
    W_readout = np.random.uniform(size=np.array([1,width]),low=-.5,high=.5)
    # Generate Matrices
    for i_weights in range(Depth_Bayesian_DNN):
        W_hidden_loop = np.random.uniform(size=np.array([width,width]),low=-.5,high=.5)
        if i_weights == 0:
            W_hidden_list = [W_hidden_loop]
        else:
            W_hidden_list.append(W_hidden_loop)
    # Define DNN Applier
    def f_unknown(x):
        x_internal = x.reshape(-1,)
        # Get fBM path
        for d in range(problem_dim):
            fBM_gen_loop = (((FBM(n=N_Euler_Steps, hurst=Hurst_Exponent, length=1, method='daviesharte')).fbm())[1:]).reshape(-1,1)
            if d == 0:
                fBM_gen = fBM_gen_loop
            else:
                fBM_gen = np.append(fBM_gen,fBM_gen_loop,axis=-1)
        # Perform Integral
        for t in range(N_Euler_Steps):
            drift_update = alpha(t/N_Euler_Steps,x_internal)/N_Euler_Steps
            vol_update = beta(t/N_Euler_Steps,x_internal)
            x_internal = x_internal + drift_update + np.matmul(vol_update,fBM_gen[t,])
        # Sum at output
        output_indicator = np.max(x_internal)
        return output_indicator

    def Simulator(x_in):
        for i_MC in range(N_Monte_Carlo_Samples):
            y_MC_loop = f_unknown(x_in)
            if i_MC == 0:
                y_MC = y_MC_loop
            else:
                y_MC = np.append(y_MC,y_MC_loop)
        return y_MC


# ## Initialize Data

# In[13]:


N_test_size = int(np.round(N_train_size*train_test_ratio,0))


# ### Initialize Training Data (Inputs)

# Try initial sampling-type implementation!  It worked nicely..i.e.: centers were given!

# In[14]:


# Get Training Set
X_train = np.random.uniform(size=np.array([N_train_size,problem_dim]),low=.5,high=1.5)

# Get Testing Set
test_set_indices = np.random.choice(range(X_train.shape[0]),N_test_size)
X_test = X_train[test_set_indices,]
X_test = X_test + np.random.uniform(low=-(delta/np.sqrt(problem_dim)), 
                                    high = -(delta/np.sqrt(problem_dim)),
                                    size = X_test.shape)


# In[15]:


# Initialize k_means
N_Quantizers_to_parameterize = int(np.maximum(2,round(Proportion_per_cluster*X_train.shape[0])))
kmeans = KMeans(n_clusters=N_Quantizers_to_parameterize, random_state=0).fit(X_train)
# Get Classes
Train_classes = np.array(pd.get_dummies(kmeans.labels_))
# Get Center Measures
Barycenters_Array_x = kmeans.cluster_centers_


# ### Get Barycenters
# *Here we make the assumption that we can directly resample $f(X=x,U)$ if necessary...or that it is available as part of the dataset.*

# In[16]:


for i in tqdm(range(Barycenters_Array_x.shape[0])):
    # Put Datum
    Bar_x_loop = Barycenters_Array_x[i,]
    # Product Monte-Carlo Sample for Input
    Bar_y_loop = (Simulator(Bar_x_loop)).reshape(1,-1)

    # Update Dataset
    if i == 0:
        Barycenters_Array = Bar_y_loop
    else:
        Barycenters_Array = np.append(Barycenters_Array,Bar_y_loop,axis=0)


# ### Initialize Training Data (Outputs)

# #### Get Training Set

# In[17]:


for i in tqdm(range(X_train.shape[0])):
    # Put Datum
    x_loop = X_train[i,]
    # Product Monte-Carlo Sample for Input
    y_loop = (Simulator(x_loop)).reshape(1,-1)

    # Update Dataset
    if i == 0:
        Y_train = y_loop
        Y_train_mean_emp = np.mean(y_loop)
    else:
        Y_train = np.append(Y_train,y_loop,axis=0)
        Y_train_mean_emp = np.append(Y_train_mean_emp,np.mean(y_loop))


# #### Get Test Set

# In[18]:


# Start Timer
Test_Set_PredictionTime_MC = time.time()

# Generate Data
for i in tqdm(range(X_test.shape[0])):
    # Put Datum
    x_loop = X_test[i,]
    # Product Monte-Carlo Sample for Input
    y_loop = (Simulator(x_loop)).reshape(1,-1)

    # Update Dataset
    if i == 0:
        Y_test = y_loop
    else:
        Y_test = np.append(Y_test,y_loop,axis=0)
        
# End Timer
Test_Set_PredictionTime_MC = time.time() - Test_Set_PredictionTime_MC


# # Train Model

# #### Start Timer

# In[19]:


# Start Timer
Type_A_timer_Begin = time.time()


# ### Train Deep Classifier

# In this step, we train a deep (feed-forward) classifier:
# $$
# \hat{f}\triangleq \operatorname{Softmax}_N\circ W_J\circ \sigma \bullet \dots \sigma \bullet W_1,
# $$
# to identify which barycenter we are closest to.

# #### Train Deep Classifier

# Re-Load Packages and CV Grid

# In[20]:


# Re-Load Hyper-parameter Grid
exec(open('CV_Grid.py').read())
# Re-Load Classifier Function(s)
exec(open('Helper_Functions.py').read())


# Train Deep Classifier

# In[21]:


print("==========================================")
print("Training Classifer Portion of Type-A Model")
print("==========================================")

# Redefine (Dimension-related) Elements of Grid
param_grid_Deep_Classifier['input_dim'] = [problem_dim]
param_grid_Deep_Classifier['output_dim'] = [N_Quantizers_to_parameterize]

# Train simple deep classifier
predicted_classes_train, predicted_classes_test, N_params_deep_classifier, timer_output = build_simple_deep_classifier(n_folds = CV_folds, 
                                                                                                        n_jobs = n_jobs, 
                                                                                                        n_iter = n_iter, 
                                                                                                        param_grid_in=param_grid_Deep_Classifier, 
                                                                                                        X_train = X_train, 
                                                                                                        y_train = Train_classes,
                                                                                                        X_test = X_test)

print("===============================================")
print("Training Classifer Portion of Type Model: Done!")
print("===============================================")


# #### Get Predicted Quantized Distributions
# - Each *row* of "Predicted_Weights" is the $\beta\in \Delta_N$.
# - Each *Column* of "Barycenters_Array" denotes the $x_1,\dots,x_N$ making up the points of the corresponding empirical measures.

# In[22]:


# Initialize Empirical Weights
empirical_weights = (np.ones(N_Monte_Carlo_Samples)/N_Monte_Carlo_Samples).reshape(-1,)

for i in range(N_Quantizers_to_parameterize):
    if i == 0:
        points_of_mass = Barycenters_Array[i,]
    else:
        points_of_mass = np.append(points_of_mass,Barycenters_Array[i,])


# In[23]:


# Get Noisless Mean
direct_facts = np.apply_along_axis(f_unknown, 1, X_train)
direct_facts_test = np.apply_along_axis(f_unknown, 1, X_test)


# #### Get Training Errors

# In[24]:


print("#--------------------#")
print(" Get Training Error(s)")
print("#--------------------#")
for i in tqdm(range((X_train.shape[0]))):
    for j in range(N_Quantizers_to_parameterize):
        b_loop = np.repeat(predicted_classes_train[i,j],N_Monte_Carlo_Samples)
        if j == 0:
            b = b_loop
        else:
            b = np.append(b,b_loop)
        b = b.reshape(-1,1)
        b = b
    b = np.array(b,dtype=float).reshape(-1,)
    b = b/N_Monte_Carlo_Samples
    
    # Compute Error(s)
    ## W1
    W1_loop = ot.emd2_1d(points_of_mass,
                         np.array(Y_train[i,]).reshape(-1,),
                         b,
                         empirical_weights)
    
    ## M1
    Mu_hat = np.sum(b*(points_of_mass))
    Mu_MC = np.mean(np.array(Y_train[i,]))
    if f_unknown_mode == "Rough_SDE":
        Mu = Mu_MC
    else:
        Mu = direct_facts[i,]
        
    ### Error(s)
    Mean_loop = (Mu_hat-Mu)
    Mean_loop_MC = (Mu_hat-Mu_MC)
    
    ## M2
    Var_hat = np.sum(((points_of_mass-Mu_hat)**2)*b)
    Var_MC = np.mean(np.array(Y_train[i]-Mu_MC)**2)
    if f_unknown_mode == "Rough_SDE":
        Var = Var_MC
    else:
        Var = np.mean((direct_facts[i,]-Mu)**2)
    
    ### Error(s)
    Var_loop = np.abs(Var_hat-Var)
    Var_loop_MC = np.abs(Var_MC-Var)
    
    # Update
    if i == 0:
        W1_errors = W1_loop
        Mean_errors =  Mean_loop
        Var_errors = Var_loop
        Mean_errors_MC =  Mean_loop_MC
        Var_errors_MC = Var_loop_MC
        
        
    else:
        W1_errors = np.append(W1_errors,W1_loop)
        Mean_errors =  np.append(Mean_errors,Mean_loop)
        Var_errors = np.append(Var_errors,Var_loop)
        Mean_errors_MC =  np.append(Mean_errors_MC,Mean_loop_MC)
        Var_errors_MC = np.append(Var_errors_MC,Var_loop_MC)
        
print("#-------------------------#")
print(" Get Training Error(s): END")
print("#-------------------------#")


# #### Get Test Errors

# In[25]:


print("#----------------#")
print(" Get Test Error(s)")
print("#----------------#")
for i in tqdm(range((X_test.shape[0]))):
    for j in range(N_Quantizers_to_parameterize):
        b_loop_test = np.repeat(predicted_classes_test[i,j],N_Monte_Carlo_Samples)
        if j == 0:
            b_test = b_loop_test
        else:
            b_test = np.append(b,b_loop)
        b_test = b_test.reshape(-1,1)
    b_test = np.array(b,dtype=float).reshape(-1,)
    b_test = b/N_Monte_Carlo_Samples
    
    # Compute Error(s)
    ## W1
    W1_loop_test = ot.emd2_1d(points_of_mass,
                         np.array(Y_test[i,]).reshape(-1,),
                         b,
                         empirical_weights)
    
    ## M1
    Mu_hat_test = np.sum(b_test*(points_of_mass))
    Mu_MC_test = np.mean(np.array(Y_test[i,]))
    if f_unknown_mode == "Rough_SDE":
        Mu_test = Mu_MC_test
    else:
        Mu_test = direct_facts_test[i,]
    Mu_test = direct_facts_test[i,]
    ### Error(s)
    Mean_loop_test = (Mu_hat_test-Mu_test)
    Mean_loop_MC_test = (Mu_hat_test-Mu_MC_test)
    
    ## M2
    Var_hat_test = np.sum(((points_of_mass-Mu_hat_test)**2)*b)
    Var_MC_test = np.mean(np.array(Y_test[i]-Mu_MC)**2)
    if f_unknown_mode == "Rough_SDE":
        Var_test = Var_MC_test
    else:
        Var_test = np.mean((direct_facts_test[i,]-Mu)**2)
    
    ### Error(s)
    Var_loop_test = np.abs(Var_hat_test-Var_test)
    Var_loop_MC_test = np.abs(Var_MC_test-Var_test)
    
    # Update
    if i == 0:
        W1_errors_test = W1_loop_test
        Mean_errors_test =  Mean_loop_test
        Var_errors_test = Var_loop_test
        Mean_errors_MC_test =  Mean_loop_MC_test
        Var_errors_MC_test = Var_loop_MC_test
        
        
    else:
        W1_errors_test = np.append(W1_errors_test,W1_loop_test)
        Mean_errors_test =  np.append(Mean_errors_test,Mean_loop_test)
        Var_errors_test = np.append(Var_errors_test,Var_loop_test)
        Mean_errors_MC_test =  np.append(Mean_errors_MC_test,Mean_loop_MC_test)
        Var_errors_MC_test = np.append(Var_errors_MC_test,Var_loop_MC_test)
        
print("#-------------------------#")
print(" Get Training Error(s): END")
print("#-------------------------#")


# #### Stop Timer

# In[26]:


# Stop Timer
Type_A_timer_end = time.time()
# Compute Lapsed Time Needed For Training
Time_Lapse_Model_A = Type_A_timer_end - Type_A_timer_Begin


# ---
# # Benchmarks
# ---

# In[36]:


# %run Benchmarks_Model_Builder.ipynb
exec(open('Benchmarks_Model_Builder.py').read())
exec(open('CV_Grid.py').read())


# Implements the Elastic-Net Regression- only predicting mean

# In[28]:


# Fit Elastic Net Model
Lin_reg.fit(X_train,Y_train_mean_emp)

# Get Predictions
ENET_predict = Lin_reg.predict(X_train)
ENET_predict_test = Lin_reg.predict(X_test)

# Get Prediction Errors
## Train
for i in range(X_train.shape[0]):
    Mu = direct_facts[i,]
    error_loop = np.abs(Mu-ENET_predict[i])
    if i == 0:
        Mean_errors_ENET = error_loop
    else:
        Mean_errors_ENET = np.append(Mean_errors_ENET,error_loop)
## Test
for i in range(X_test.shape[0]):
    Mu_test = direct_facts[i,]
    error_loop_test = np.abs(Mu-ENET_predict_test[i])
    if i == 0:
        Mean_errors_ENET_test = error_loop_test
    else:
        Mean_errors_ENET_test = np.append(Mean_errors_ENET_test,error_loop_test)


# ### Kernel Ridge Regression

# In[29]:


Xhat_Kridge, Xhat_Kridge_test , relic = get_Kernel_Ridge_Regressor(X_train,X_test,Y_train_mean_emp)


# Get Prediction Errors
## Train
for i in range(X_train.shape[0]):
    Mu = direct_facts[i,]
    error_loop = np.abs(Mu-Xhat_Kridge[i])
    if i == 0:
        Mean_errors_KRidge = error_loop
    else:
        Mean_errors_KRidge = np.append(Mean_errors_KRidge,error_loop)
## Test
for i in range(X_test.shape[0]):
    Mu_test = direct_facts[i,]
    error_loop_test = np.abs(Mu-Xhat_Kridge_test[i])
    if i == 0:
        Mean_errors_KRidge_test = error_loop_test
    else:
        Mean_errors_KRidge_test = np.append(Mean_errors_KRidge_test,error_loop_test)


# ## Gradient-Boosted Random Forest Regressor

# In[30]:


GBRF_y_hat_train, GBRF_y_hat_test, GBRF_model = get_GBRF(X_train,X_test,Y_train_mean_emp)

# Get Prediction Errors
## Train
for i in range(X_train.shape[0]):
    Mu = direct_facts[i,]
    error_loop = np.abs(Mu-GBRF_y_hat_train[i])
    if i == 0:
        Mean_errors_GBRF = error_loop
    else:
        Mean_errors_GBRF = np.append(Mean_errors_GBRF,error_loop)
## Test
for i in range(X_test.shape[0]):
    Mu_test = direct_facts[i,]
    error_loop = np.abs(Mu-GBRF_y_hat_test[i])
    if i == 0:
        Mean_errors_GBRF_test = error_loop_test
    else:
        Mean_errors_GBRF_test = np.append(Mean_errors_GBRF_test,error_loop_test)


# ## Feed-Forward (Vanilla)

# In[31]:


# Redefine (Dimension-related) Elements of Grid
param_grid_Deep_Classifier['input_dim'] = [problem_dim]
param_grid_Deep_Classifier['output_dim'] = [1]

YHat_ffNN, YHat_ffNN_test = build_ffNN(n_folds = CV_folds,
                                              n_jobs = n_jobs, 
                                              n_iter = n_iter, 
                                              param_grid_in = param_grid_Deep_Classifier,  
                                              X_train = X_train, 
                                              y_train = Y_train_mean_emp,
                                              X_test = X_test)


# Get Prediction Errors
## Train
for i in range(X_train.shape[0]):
    Mu = direct_facts[i,]
    error_loop = np.abs(Mu-YHat_ffNN[i])
    if i == 0:
        Mean_errors_ffNN = error_loop
    else:
        Mean_errors_ffNN = np.append(Mean_errors_ffNN,error_loop)
## Test
for i in range(X_test.shape[0]):
    Mu_test = direct_facts[i,]
    error_loop = np.abs(Mu-YHat_ffNN_test[i])
    if i == 0:
        Mean_errors_ffNN_test = error_loop_test
    else:
        Mean_errors_ffNN_test = np.append(Mean_errors_ffNN_test,error_loop_test)


# # Summary of Mean-Centric Regression Models

# In[32]:


Summary_mean_models = pd.DataFrame({"M1":np.array([np.mean(np.abs(Mean_errors)),np.mean(np.abs(Mean_errors_test))]),
                                    "M1_MC":np.array([np.mean(np.abs(Mean_errors_MC)),np.mean(np.abs(Mean_errors_MC_test))]),
                                    "M1_ENET":np.array([np.mean(np.abs(Mean_errors_ENET)),np.mean(np.abs(Mean_errors_ENET_test))]),
                                    "M1_KRidge":np.array([np.mean(np.abs(Mean_errors_KRidge)),np.mean(np.abs(Mean_errors_KRidge_test))]),
                                    "M1_GBRFR":np.array([np.mean(np.abs(Mean_errors_GBRF)),np.mean(np.abs(Mean_errors_GBRF_test))]),
                                    "M1_ffNN":np.array([np.mean(np.abs(Mean_errors_ffNN)),np.mean(np.abs(Mean_errors_ffNN_test))])
                                   },index=["Train","Test"])

print(Summary_mean_models)


# ---
# 
# ---
# 
# ---

# ## Get Moment Predictions

# #### Write Predictions

# ### Training-Set Result(s): 

# In[33]:


#---------------------------------------------------------------------------------------------#
W1_95 = bootstrap(W1_errors, n=1000, func=np.mean)(.95)
W1_99 = bootstrap(W1_errors, n=1000, func=np.mean)(.99)
#---------------------------------------------------------------------------------------------#
Model_Complexity = pd.DataFrame({"N_Centers":N_Quantizers_to_parameterize,
                                 "N_Q":N_Monte_Carlo_Samples,
                                 "N_Params":N_params_deep_classifier,
                                 "Training Time":Time_Lapse_Model_A,
                                 "T_Test/T_Test-MC": (timer_output/Test_Set_PredictionTime_MC),
                                 "Time Test": timer_output,
                                 "Time EM-MC": Test_Set_PredictionTime_MC},index=["Model_Complexity_metrics"])

#---------------------------------------------------------------------------------------------#
# Compute Error Statistics/Descriptors
Summary = pd.DataFrame({"W1":np.array([np.mean(np.abs(W1_errors)),np.mean(np.abs(W1_errors_test))]),
                        "M1":np.array([np.mean(np.abs(Mean_errors)),np.mean(np.abs(Mean_errors_test))]),
                        "M1_MC":np.array([np.mean(np.abs(Mean_errors_MC)),np.mean(np.abs(Mean_errors_MC_test))]),
                        "Var":np.array([np.mean(np.abs(Var_errors)),np.mean(np.abs(Var_errors_test))]),
                        "Var_MC":np.array([np.mean(np.abs(Var_errors_MC)),np.mean(np.abs(Var_errors_MC_test))]),                                             
                        "N_Centers":np.array((N_Quantizers_to_parameterize,N_Quantizers_to_parameterize)),
                        "N_Q":np.array((N_Monte_Carlo_Samples,N_Monte_Carlo_Samples)),
                        "N_Params":np.array((N_params_deep_classifier,N_params_deep_classifier)),
                        "Training Time":np.array((Time_Lapse_Model_A,Time_Lapse_Model_A)),
                        "T_Test/T_Test-MC":np.array(((timer_output/Test_Set_PredictionTime_MC),(timer_output/Test_Set_PredictionTime_MC))),
                        "Problem_Dimension":np.array((problem_dim,problem_dim))
                       },index=["Train","Test"])


# Write Performance Metrics to file #
#-----------------------------------#
pd.set_option('display.float_format', '{:.4E}'.format)
Model_Complexity.to_latex((results_tables_path+"Latent_Width_NSDE"+str(width)+"Problemdimension"+str(problem_dim)+"__ModelComplexities.tex"))
pd.set_option('display.float_format', '{:.4E}'.format)
Summary.to_latex((results_tables_path+"Latent_Width_NSDE"+str(width)+"Problemdimension"+str(problem_dim)+"__SUMMARY_METRICS.tex"))


#---------------------------------------------------------------------------------------------#
# Update User
print(Model_Complexity)
print(Summary)


# # Update User

# ## Prediction Quality

# In[34]:


Summary


# # Performance wrt Mean Prediction

# In[35]:


Summary_mean_models


# ---

# ---
# # Fin
# ---

# ---
