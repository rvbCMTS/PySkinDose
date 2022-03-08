# Background

X-ray-induced skin injuries may occur due to high absorbed patient skin doses from complex 
_fluoroscopically guided interventions_ (FGI). This requires suitable action levels for patient-specific 
follow-up. Metrics such as fluoroscopy time, air kerma-area product, or the number of _digital 
subtraction angiography_ (DSA) runs have historically been used for radiation monitoring of patient 
exposure. These metrics lack correlation to X-ray beam quality, variable pulse rates, dose rates, 
patient size and the geometrical factors that greatly influence skin dose.

A directly available metric for _quality assurance_ (QA) of patient dose is the cumulative air kerma. 
This exposure value is referenced to a specific location, the _patient entrance reference point_ 
(PERP). This reference point is located along the central X-ray beam, commonly but not always at a 
distance of 15 cm from the isocenter in the direction of the X-ray tube. The cumulative air kerma 
has been available on most interventional C-arm X-ray equipment since 2006 when it became mandated by the 
FDA. However, the cumulative air kerma also has known limitations, e.g. patient skin positioning in 
relation to the PERP, beam attenuation of the patient table and pad, influence of scattered radiation 
etc. The currently (year 2022) most useful metric to indicate a risk of erythema, epilation or greater skin injury 
that also include actionable information is the _peak skin dose_ (PSD), which gives the largest dose to 
a region of skin.

Compared to other X-ray modalities, the greatest challenge in estimating patient dose metrics may be 
found for C-arm fluoroscopy equipment, particularly for FGI procedures. This is due to complex 
geometries, accuracy in representing patient position and dealing with uncertainty in metrics. There 
are many different solutions that can be used for estimating skin dose, including commercial, 
non-commercial and open-source. Many of these solutions are great tools but do not offer the user 
a chance to analyze the effect of all the variables, add functionality and improve uncertainties with 
in-house measurements. **P**y**S**kin**D**ose aims to be an open-source tool for estimation of PSD 
with full transparency and user adoption functionality.