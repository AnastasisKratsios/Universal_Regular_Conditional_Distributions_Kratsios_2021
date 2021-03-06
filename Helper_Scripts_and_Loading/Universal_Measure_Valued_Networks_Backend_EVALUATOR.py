#!/usr/bin/env python
# coding: utf-8

# # Model Evaluator for DMN

# ---

# #### Get Predicted Quantized Distributions
# - Each *row* of "Predicted_Weights" is the $\beta\in \Delta_N$.
# - Each *Column* of "Barycenters_Array" denotes the $x_1,\dots,x_N$ making up the points of the corresponding empirical measures.

# In[ ]:


# if f_unknown_mode != "Rough_SDE":
#     for i in range(Barycenters_Array.shape[0]):
#         if i == 0:
#             points_of_mass = Barycenters_Array[i,]
#         else:

#             points_of_mass = np.append(points_of_mass,Barycenters_Array[i,])
# else:
#     for i in range(Barycenters_Array.shape[0]):
#         if i == 0:
#             points_of_mass = Barycenters_Array[i,]
#         else:

#             points_of_mass = np.append(points_of_mass,Barycenters_Array[i,],axis=0)


# #### Get Perfect Oracle (i.e.: closed-form mean)
# Note, this is only available in certain settings; and not the ones considered in the paper.

# In[ ]:


# if (f_unknown_mode != "GD_with_randomized_input") and (f_unknown_mode != "Rough_SDE") and (f_unknown_mode != "Extreme_Learning_Machine") and (f_unknown_mode != "Rough_SDE_Vanilla"):
#     # Get Noisless Mean
#     direct_facts = np.apply_along_axis(f_unknown, 1, X_train)
#     direct_facts_test = np.apply_along_axis(f_unknown, 1, X_test)


# ## Get Error(s)

# In[ ]:


# %run Evaluation.ipynb
exec(open('Helper_Scripts_and_Loading/Evaluation.py').read())


# #### Initialize Relevant Solvers
# Solve using either:
# - Sinkhorn Regularized Wasserstein Distance of: [Cuturi - Sinkhorn Distances: Lightspeed Computation of Optimal Transport (2016)](https://papers.nips.cc/paper/2013/hash/af21d0c97db2e27e13572cbf59eb343d-Abstract.html)
# - Slices Wasserstein Distance of: [Bonneel, Nicolas, et al. “Sliced and radon wasserstein barycenters of measures.” Journal of Mathematical Imaging and Vision 51.1 (2015): 22-45](https://dl.acm.org/doi/10.1007/s10851-014-0506-3)

# In[ ]:


# Transport-problem initializations #
#-----------------------------------#
if output_dim != 1:
    ## Multi-dimensional
    # Externally Update Empirical Weights for multi-dimensional case
    empirical_weights = np.full((N_Monte_Carlo_Samples,),1/N_Monte_Carlo_Samples)
    # Also Initialize
    Sinkhorn_regularization = 0.1
else:
    ## Single-Dimensional
    # Initialize Empirical Weights
    empirical_weights = (np.ones(N_Monte_Carlo_Samples)/N_Monte_Carlo_Samples).reshape(-1,)

#-------------------------#
# Define Transport Solver #
#-------------------------#
def transport_dist(x_source,w_source,x_sink,w_sink,output_dim,OT_method="Sliced",n_projections = 10):
    # Decide which problem to solve (1D or multi-D)?
    if output_dim == 1:
        OT_out = ot.emd2_1d(x_source,
                            x_sink,
                            w_source,
                            w_sink)
    else:
        # COERCSION
        ## Update Source Distribution
        x_source = points_of_mass.reshape(-1,output_dim)
        ## Update Sink Distribution
        x_sink = np.array(Y_train[i,]).reshape(-1,output_dim)
        
        if OT_method == "Sinkhorn":
            OT_out = ot.bregman.empirical_sinkhorn2(X_s = x_source, 
                                                    X_t = x_sink,
                                                    a = w_source, 
                                                    b = w_sink, 
                                                    reg=0.01, 
                                                    verbose=False,
                                                    method = "sinkhorn_stabilized")
            # COERSION
            OT_out = float(OT_out[0])
        else:
            OT_out = ot.sliced.sliced_wasserstein_distance(X_s = x_source, 
                                                           X_t = x_sink,
                                                           a = w_source, 
                                                           b = w_sink, 
                                                           seed = 2020,
                                                           n_projections = n_projections)
            # COERSION
            OT_out = float(OT_out)
    # Return (regularized?) Transport Distance
    return OT_out


# #### Compute *Training* Error(s)

# In[ ]:


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
    b = b/np.sum(b)
    
    # Compute Error(s)
    ## W1
    W1_loop = transport_dist(x_source = points_of_mass,
                             w_source = b,
                             x_sink = np.array(Y_train[i,]).reshape(-1,),
                             w_sink = empirical_weights,
                             output_dim = output_dim,
                             OT_method="proj",
                             n_projections = 100)
    
    ## M1
    Mu_hat = np.matmul(points_of_mass.T,b).reshape(-1,)
    Mu_MC = np.mean(np.array(Y_train[i,]),axis=0).reshape(-1,)
    if f_unknown_mode == "Heteroskedastic_NonLinear_Regression":
        Mu = direct_facts[i,]
    else:
        Mu = Mu_MC
    ## Tally W1-Related Errors
    ## Mu
    Mean_loop = np.sum(np.abs((Mu_hat-Mu)))
    Mean_loop_MC = np.sum(np.abs((Mu-Mu_MC)))
    
    if (f_unknown_mode != "Rough_SDE") and (f_unknown_mode != "Rough_SDE_Vanilla"):
        ## Variance
        Var_hat = np.sum(((points_of_mass-Mu_hat)**2)*b)
        Var_MC = np.mean(np.array(Y_train[i]-Mu_MC)**2)
        if f_unknown_mode == "Heteroskedastic_NonLinear_Regression":
            Var = 2*np.sum(X_train[i,]**2)
        else:
            Var = Var_MC     

        # Skewness
        Skewness_hat = np.sum((((points_of_mass-Mu_hat)/Var_hat)**3)*b)
        Skewness_MC = np.mean((np.array(Y_train[i]-Mu_MC)/Var_MC)**3)
        if f_unknown_mode == "Heteroskedastic_NonLinear_Regression":
            Skewness = 0
        else:
            Skewness = Skewness_MC

        # Excess Kurtosis
        Ex_Kurtosis_hat = np.sum((((points_of_mass-Mu_hat)/Var_hat)**4)*b) - 3
        Ex_Kurtosis_MC = np.mean((np.array(Y_train[i]-Mu_MC)/Var_MC)**4) - 3
        if f_unknown_mode == "Heteroskedastic_NonLinear_Regression":
            Ex_Kurtosis = 3
        else:
            Ex_Kurtosis = Ex_Kurtosis_MC
        # Tally Higher-Order Error(s)
        ## Var
        Var_loop = np.sum(np.abs(Var_hat-Var))
        Var_loop_MC = np.sum(np.abs(Var_MC-Var))
        ## Skewness
        Skewness_loop = np.abs(Skewness_hat-Skewness)
        Skewness_loop_MC = np.abs(Skewness_MC-Skewness)
        ## Excess Kurtosis
        Ex_Kurtosis_loop = np.abs(Ex_Kurtosis-Ex_Kurtosis_hat)
        Ex_Kurtosis_loop_MC = np.abs(Ex_Kurtosis-Ex_Kurtosis_MC)
    
    
    # Update
    if i == 0:
        W1_errors = W1_loop
        ## DNM
        Mean_errors =  Mean_loop
        ## Monte-Carlo
        Mean_errors_MC =  Mean_loop_MC
        # Higher-Order Moments
        if (f_unknown_mode != "Rough_SDE") and (f_unknown_mode != 'Rough_SDE_Vanilla'):
            ## DNM
            Var_errors = Var_loop
            Skewness_errors = Skewness_loop
            Ex_Kurtosis_errors = Ex_Kurtosis_loop
            ## Monte-Carlo
            Mean_errors_MC =  Mean_loop_MC
            Var_errors_MC = Var_loop_MC
            Skewness_errors_MC = Skewness_loop_MC
            Ex_Kurtosis_errors_MC = Ex_Kurtosis_loop_MC
        
        
    else:
        W1_errors = np.append(W1_errors,W1_loop)
        # Moments
        ## DNM
        Mean_errors =  np.append(Mean_errors,Mean_loop)
        ## Monte-Carlo
        Mean_errors_MC =  np.append(Mean_errors_MC,Mean_loop_MC)
        ## Higher-Order Moments
        if (f_unknown_mode != "Rough_SDE") and (f_unknown_mode != 'Rough_SDE_Vanilla'):
            ## DNM
            Var_errors = np.append(Var_errors,Var_loop)
            Skewness_errors = np.append(Skewness_errors,Skewness_loop)
            Ex_Kurtosis_errors = np.append(Ex_Kurtosis_errors,Ex_Kurtosis_loop)
            ## Monte-Carlo
            Var_errors_MC = np.append(Var_errors_MC,Var_loop_MC)
            Skewness_errors_MC = np.append(Skewness_errors_MC,Skewness_loop_MC)
            Ex_Kurtosis_errors_MC = np.append(Ex_Kurtosis_errors_MC,Ex_Kurtosis_loop_MC)
            

## Get Error Statistics
W1_Errors = np.array(bootstrap(np.abs(W1_errors),n=N_Boostraps_BCA)(.95))
Mean_Errors =  np.array(bootstrap(np.abs(Mean_errors),n=N_Boostraps_BCA)(.95))
Mean_Errors_MC =  np.array(bootstrap(np.abs(Mean_errors_MC),n=N_Boostraps_BCA)(.95))
print("#-------------------------#")
print(" Get Training Error(s): END")
print("#-------------------------#")


# #### Compute *Testing* Errors

# In[ ]:


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
    W1_loop_test = transport_dist(x_source = points_of_mass,
                                  w_source = b,
                                  x_sink = np.array(Y_test[i,]).reshape(-1,),
                                  w_sink = empirical_weights,
                                  output_dim = output_dim)
    
    ## M1
    Mu_hat_test = np.matmul(points_of_mass.T,b).reshape(-1,)
    Mu_MC_test = np.mean(np.array(Y_test[i,]),axis=0).reshape(-1,)
    if f_unknown_mode == "Heteroskedastic_NonLinear_Regression":
        Mu_test = direct_facts_test[i,]
    else:
        Mu_test = Mu_MC_test
    ## Tally W1-Related Errors
    ## Mu
    Mean_loop_test = np.sum(np.abs((Mu_hat_test-Mu_test)))
    Mean_loop_MC_test = np.sum(np.abs((Mu_test-Mu_MC_test)))
    
    if (f_unknown_mode != "Rough_SDE") and (f_unknown_mode != "Rough_SDE_Vanilla"):
        ## M2
        Var_hat_test = np.sum(((points_of_mass-Mu_hat_test)**2)*b)
        Var_MC_test = np.mean(np.array(Y_test[i]-Mu_MC)**2)
        if f_unknown_mode == "Rough_SDE":
            Var_test = 2*np.sum(X_test[i,]**2)
        else:
            Var_test = Var_MC

        ### Error(s)
        Var_loop_test = np.abs(Var_hat_test-Var_test)
        Var_loop_MC_test = np.abs(Var_MC_test-Var_test)

        # Skewness
        Skewness_hat_test = np.sum((((points_of_mass-Mu_hat_test)/Var_hat_test)**3)*b)
        Skewness_MC_test = np.mean((np.array(Y_test[i]-Mu_MC_test)/Var_MC_test)**3)
        if f_unknown_mode == "Heteroskedastic_NonLinear_Regression":
            Skewness_test = 0
        else:
            Skewness_test = Skewness_MC_test
        ### Error(s)
        Skewness_loop_test = np.abs(Skewness_hat_test-Skewness_test)
        Skewness_loop_MC_test = np.abs(Skewness_MC_test-Skewness_test)

        # Skewness
        Ex_Kurtosis_hat_test = np.sum((((points_of_mass-Mu_hat_test)/Var_hat_test)**4)*b) - 3
        Ex_Kurtosis_MC_test = np.mean((np.array(Y_test[i]-Mu_MC_test)/Var_MC_test)**4) - 3
        if f_unknown_mode == "Heteroskedastic_NonLinear_Regression":
            Ex_Kurtosis_test = 3
        else:
            Ex_Kurtosis_test = Ex_Kurtosis_MC_test
        ### Error(s)
        Ex_Kurtosis_loop_test = np.abs(Ex_Kurtosis_test-Ex_Kurtosis_hat_test)
        Ex_Kurtosis_loop_MC_test = np.abs(Ex_Kurtosis_test-Ex_Kurtosis_MC_test)
    
    
    # Update
    if i == 0:
        W1_errors_test = W1_loop_test
        ## DNM
        Mean_errors_test =  Mean_loop_test
        ## Monte-Carlo
        Mean_errors_MC_test =  Mean_loop_MC_test
        ### Get Higher-Moments
        if (f_unknown_mode != "Rough_SDE") and (f_unknown_mode != 'Rough_SDE_Vanilla'):
            ## DNM
            Var_errors_test = Var_loop_test
            Skewness_errors_test = Skewness_loop_test
            Ex_Kurtosis_errors_test = Ex_Kurtosis_loop_test
            ## Monte-Carlo
            Var_errors_MC_test = Var_loop_MC_test
            Skewness_errors_MC_test = Skewness_loop_MC_test
            Ex_Kurtosis_errors_MC_test = Ex_Kurtosis_loop_MC_test
            
        
    else:
        W1_errors_test = np.append(W1_errors_test,W1_loop_test)
        ## DNM
        Mean_errors_test =  np.append(Mean_errors_test,Mean_loop_test)
        ## Monte-Carlo
        Mean_errors_MC_test =  np.append(Mean_errors_MC_test,Mean_loop_MC_test)
        ### Get Higher Moments
        if (f_unknown_mode != "Rough_SDE") and (f_unknown_mode != 'Rough_SDE_Vanilla'):
            Var_errors_test = np.append(Var_errors_test,Var_loop_test)
            Skewness_errors_test = np.append(Skewness_errors_test,Skewness_loop_test)
            Ex_Kurtosis_errors_test = np.append(Ex_Kurtosis_errors_test,Ex_Kurtosis_loop_test)
            ## Monte-Carlo
            Var_errors_MC_test = np.append(Var_errors_MC_test,Var_loop_MC_test)
            Skewness_errors_MC_test = np.append(Skewness_errors_MC_test,Skewness_loop_MC_test)
            Ex_Kurtosis_errors_MC_test = np.append(Ex_Kurtosis_errors_MC_test,Ex_Kurtosis_loop_MC_test)

            
## Get Error Statistics
W1_Errors_test = np.array(bootstrap(np.abs(W1_errors_test),n=N_Boostraps_BCA)(.95))
Mean_Errors_test =  np.array(bootstrap(np.abs(Mean_errors_test),n=N_Boostraps_BCA)(.95))
Mean_Errors_MC_test =  np.array(bootstrap(np.abs(Mean_errors_MC_test),n=N_Boostraps_BCA)(.95))
print("#------------------------#")
print(" Get Testing Error(s): END")
print("#------------------------#")


# #### Stop Timer

# In[ ]:


# Stop Timer
Type_A_timer_end = time.time()
# Compute Lapsed Time Needed For Training
Time_Lapse_Model_DNM = Type_A_timer_end - Type_A_timer_Begin


# ## Update Tables

# #### Predictive Performance Metrics

# In[ ]:


Summary_pred_Qual_models = pd.DataFrame({"DNM":np.append(np.append(W1_Errors,
                                                                   Mean_Errors),
                                                         np.array([N_params_deep_classifier,
                                                                   Time_Lapse_Model_DNM,
                                                                   (timer_output/Test_Set_PredictionTime_MC)])),
                                    "MC-Oracle":np.append(np.append(np.repeat(0,3),
                                                                   Mean_Errors_MC),
                                                         np.array([0,
                                                                   Train_Set_PredictionTime_MC,
                                                                   (Test_Set_PredictionTime_MC/Test_Set_PredictionTime_MC)])),
                                   },index=["W1-95L","W1","W1-95R","M-95L","M","M-95R","N_Par","Train_Time","Test_Time/MC-Oracle_Test_Time"])

Summary_pred_Qual_models_test = pd.DataFrame({"DNM":np.append(np.append(W1_Errors_test,
                                                                   Mean_Errors_test),
                                                         np.array([N_params_deep_classifier,
                                                                   Time_Lapse_Model_DNM,
                                                                   (timer_output/Test_Set_PredictionTime_MC)])),
                                    "MC-Oracle":np.append(np.append(np.repeat(0,3),
                                                                   Mean_Errors_MC_test),
                                                         np.array([0,
                                                                   Train_Set_PredictionTime_MC,
                                                                   (Test_Set_PredictionTime_MC/Test_Set_PredictionTime_MC)])),
                                   },index=["W1-95L","W1","W1-95R","M-95L","M","M-95R","N_Par","Train_Time","Test_Time/MC-Oracle_Test_Time"])
## Get Worst-Case
Summary_pred_Qual_models_train = Summary_pred_Qual_models
Summary_pred_Qual_models_internal = Summary_pred_Qual_models.copy()
Summary_pred_Qual_models = np.maximum(Summary_pred_Qual_models_internal,Summary_pred_Qual_models_test)
## Write Performance Metrics
Summary_pred_Qual_models.to_latex((results_tables_path+"Performance_metrics_Problem_Type_"+str(f_unknown_mode)+"Problemdimension"+str(problem_dim)+"__SUMMARY_METRICS.tex"))
Summary_pred_Qual_models_train.to_latex((results_tables_path+"Performance_metrics_Problem_Type_"+str(f_unknown_mode)+"Problemdimension"+str(problem_dim)+"__SUMMARY_METRICS_train.tex"))
Summary_pred_Qual_models_test.to_latex((results_tables_path+"Performance_metrics_Problem_Type_"+str(f_unknown_mode)+"Problemdimension"+str(problem_dim)+"__SUMMARY_METRICS_test.tex"))


# # Update User

# In[ ]:


print(Summary_pred_Qual_models_test)
Summary_pred_Qual_models_test


# ---
# ---
# # Fin
# ---
# ---
