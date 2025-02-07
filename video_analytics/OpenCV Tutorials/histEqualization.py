
import cv2
import numpy as np
from matplotlib import pyplot as plt

img = cv2.imread('bird.png' , 0)
plt.subplot(2,2,1)
plt.imshow(img, cmap='gray')

hist, bins = np.histogram(img.flatten(),256,[0,256])  # Frequencies, values
cdf = hist.cumsum()  # Cumulative frequency values
cdf_normalized = cdf * hist.max()/ cdf.max()
# hist.max(): highest frequency (mode)
# cdf.max(): sum total
# This is so maximum of hist matches cdf

# Plots original CDF/Image
plt.subplot(2, 2, 2)
plt.plot(cdf_normalized, color = 'b')
plt.hist(img.flatten(),256,[0,256], color = 'r')
plt.xlim([0,256])
plt.legend(('cdf','histogram'), loc = 'upper left')

# Creates a masked array and makes range 0 to 255
cdf_m = np.ma.masked_equal(cdf,0)
cdf_m = (cdf_m - cdf_m.min())*255/(cdf_m.max()-cdf_m.min())
cdf = np.ma.filled(cdf_m,0).astype('uint8')
img2 = cdf[img]

# Plots transformed image
plt.subplot(2,2,3)
plt.imshow(img2, cmap='gray')

# Plots new Hist/CDF. Note this is more uniform b/c gaps between frequent bins.
plt.subplot(2,2,4)
hist2, _ = np.histogram(img2.flatten(),256,[0,256])
cdf2 = hist2.cumsum() * hist2.max()/ hist2.cumsum().max()
plt.plot(cdf2, color = 'b')
plt.hist(img2.flatten(),256,[0,256], color = 'r')
plt.xlim([0,256])
plt.legend(('cdf','histogram'), loc = 'upper left')
plt.show()

# Useful in facial recognition to make all training images have same lighting conditions.
# Shorter code: cv2.equalizeHist(img)

# Can also use a clache object. This normalizes in a 8x8 grid. Clip limit is for noise.
# clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
# cl1 = clahe.apply(img)
# cv2.imwrite('clahe_2.jpg',cl1)
