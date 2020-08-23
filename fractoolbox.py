# ============================
# fractoolbox Function Library
# ============================
'''
Python tools for structural geology and borehole image analysis that includes 
data handling, frequency and geometric analysis, and reservoir geomechanics.

Content
-------
Library content by section (and status)
-   Convert Fracture Data Format (started)
-   Geometric Sample Bias: Isogenic Contours (to come)
-   Geomechanical Models (to come)
-   3DMohr Plot Analysis (to come)

Contributions
-------------
Initiated by Irene Wallis https://github.com/ICWallis/fractoolbox
as part of Doctoral Research at the University of Auckland that is 
supervised by David Dempsey https://github.com/ddempsey and 
Julie (JR) Rowland, with math/code contributions from Evert Durán 
https://github.com/edur409.

Citations
---------
Barton, C. A., Zoback, M. D., and Moos, D., 1995, Fluid flow along 
    potentially active faults in crystalline rock: Geology, v. 23, 
    p. 683-686.

Peška, P., and Zoback, M. D., 1995, Compressive and tensile failure 
    of inclined well bores and determination of in situ stress and 
    rock strength: Journal of Geophysical Research: Solid Earth, 
    v. 100, no. B7, p. 12791-12811.

Priest, S., 1993, Discontinuity Analysis for Rock Engineering, 
    Netherlands, Springer.

Terzaghi, R. D., 1965, Sources of error in joint surveys: Geotechnique, 
    v. 15, no. 3, p. 287-304.

Wallis, I.C., Rowland, J. V. and Dempsey, D. E., Allan, G., Sidik, R., 
    Martikno, R., McLean, K., Sihotang, M., Azis, M. and Baroek, M. 
    2020 (submitted) Approaches to imaging feedzone diversity with 
    case studies from Sumatra, Indonesia, and the Taupō Volcanic Zone, 
    New Zealand. New Zealand Geothermal Workshop: Waitangi, New Zealand.

Zoback, M. D., 2010, Reservoir Geomechanics, Cambridge University Presss

Licence 
-------
fractoolbox is distributed under an Apache 2.0 licence

https://choosealicense.com/licenses/apache-2.0/

'''
# ============================
# Convert Fracture Data Format
# ============================
'''
Tools to convert between the various ways fracture geometry are described

Data Format Examples 
--------------------
The following examples all using the same fracture plane

    Borehole image log analysis:
    -   dip magnitude and dip azimuth
        Format example: dip = 30, dipaz = 350

    Structural geology:
    -   strike (0-360 degrees) and dip (0-90 degrees), using the right-hand rule
        Format example: 260/30

    -   strike (0-180 degrees), dip (0-90 degrees), and dip direction (East or West)
        Format example: 80/30/W

Refer to stereonet-basics.ipynb for visual examples, 
including how to describe and plot a line or rake

The Right-Hand Rule
-------------------
Place your right hand on the fracture plane with fingers pointed down
the direction of dip. Your thumb points to the strike azimuth which is
used under the right-hand rule convention. 
'''

def dip2strike(dipaz):
    '''Convert dip-dipazimuth data to strike using the right-hand rule

    Args:
        dipaz: Azimuth of dip in degrees from north
    
    Returns: 
        Strike azimuth (0-360 degrees) based on the right hand rule
 
    '''
    if dipaz < 90:
        strike=(dipaz-90)+360
    else:
        strike=dipaz-90
    return strike


def strike2dipaz(strike):
    '''Convert strike to dip azimuth using the right-hand rule convention

    Args:
        strike: Strike azimuth in degrees from north 
            where the right-hand rule is observed
 
    Returns
        Azimuth of the dip direction (0-360 degrees)
    
    '''
    if strike > 270:
        dipaz=(strike+90)-360
    else:
        dipaz=strike+90
    return dipaz

# ========================================
# Geometric Sample Bias: Isogenic Contours
# ========================================
'''
Seminal work by Terzaghi (1965) revealed a geometric bias generated 
by sampling a three-dimensional fracture network with a line. 
Simply put, fractures planes that are perpendicular to the line are 
very likely to be intersected whereas those parallel to the line are 
almost never intersected. This geometric sample bias generates a 'blind
zone' in fracture datasets where those which are near-parallel to the
scan-line or well-path are rarely sampled. This blind zone is 
sometimes also referred to as the 'well shadow'.

Terzaghi (1965) proposed a methodology quantifies the geometric sample 
bias using the acute angle (alpha) between the fracture plane and 
the line. Visualising the blind zone (where sin(alpha) +/- 0.3) and 
contours of sample bias (isogenic contours) on a stereonet enables
us to visually evaluate the degree that geometric sample bias in 
affects a fracture dataset.  

A weighting may be applied based on the alpha angle which may correct
the sampled fracture population to something more reflective of actual
frequency. This kind of correction is common-place in modern image log
analysis and some form of the Terzaghi correction comes baked into 
most log analysis software. However, there are two key issues with these
corrections:

-   Correction may mislead interpretation by emphasising solitary 
    fractures that are not part of some significant but under-sampled 
    population, especially where the weighting factor approaches 
    infinity near sin α = 0. Priest (1993) recommends resolving this 
    by using an upper limit of sin α = 0.1 when weighting.

-   Correction can only be applied to those fractures which were sampled
    and therefore does a poor job of correcting in the blind zone where
    fractures are rarely sampled. 

Functions are included below that (1) weight fracture populations to 
reduce the impact of geometric sample bias and (2) construct isogenic 
contours for stereonets so the effect of sample bias and the blind 
zone are visible to the interpreter. Refer to Wallis et al. (2020)
for examples of these methods as applied micro-resistivity image 
logs acquired in seven high-temperature geothermal wells.

Refer to geometric-sample-bias.ipynb for an illustration of the 
alpha angles, code examples using the functions, and plots that show
the impact of the blind zone on a range of well data. 
'''

def isogeniccontour(wpl, waz, sin_al):
    '''
    Method that parametrically generates an isogenic contour
    '''
    # Convert well azumuth/plunge to a vector p
    # calls the three functions above
    p = np.array([f(waz,wpl) for f in [unitvectorx, unitvectory, unitvectorz]])
    #print('p =', p, '\n')
    # make unit vector n1 that is perpendicular to p
    # start with a random vector
    n1 = np.random.rand(3)-0.5
    # subtract the component parallel to p to create a perpendicular vector 
    n1 -= np.dot(n1,p)*p
    # normalise to make it a unit vector
    n1 = n1/np.sqrt(np.dot(n1,n1))
    # make a second vector n2 that is perpendicular to both p and n1
    n2 = np.cross(p,n1)
    # n1 and n2 now span a plane n that is normal to p
    # find the point c where the plane n intersects the vector p for the given sin(alpha) sin_al
    cos_al = np.cos(np.arcsin(sin_al)) 
    # Scale the radius of the circle to sin(alpha)
    # produces a list of vectors that ascribe the circle
    ns = []
    for th in np.linspace(0, 2*np.pi, 1000):
        ns.append(sin_al*p+cos_al*(np.cos(th)*n1+np.sin(th)*n2))
    ns = np.array(ns)
    # checks if they are unit vectors
    #print(np.sqrt(ns[:,0]**2+ns[:,1]**2+ ns[:,2]**2)) 
    # convert ns to azumuth/plunge (strike/dip) so they can be plotted on a stereonet
    strike, dip = mplstereonet.vector2pole(ns[:,0], ns[:,1], ns[:,2])
    return strike,dip
   
# the following functions are the 'adapted' method to make the isogenic contours work
def unitvectorx(az,pl):
    #Calculate the unit vector for a pole or well path
    #Input the pole/well azumuth and plunge
    #Output the unit vector x component
    x = -1 * np.sin(np.deg2rad(az)) * np.cos(np.deg2rad(pl))
    return x

def unitvectory(az,pl):
    #Calculate the unit vector for a pole or well path
    #Input the pole/well azumuth and plunge
    #Output the unit vector y component
    y = -1 * np.cos(np.deg2rad(az)) * np.cos(np.deg2rad(pl))
    return y

def unitvectorz(az,pl):
    #Calculate the unit vector for a pole or well path
    #Input the pole/well azumuth and plunge
    #Output the unit vector z component
    z = 1 * np.sin(np.deg2rad(pl))
    return z


# ====================
# Geomechanical Models
# ====================
'''

'''
# ====================
# 3DMohr Plot Analysis
# ====================
'''

'''
