import cv2
import numpy as np
import PIL
import os
from PIL import Image, ImageEnhance
img = cv2.imread("img6.jpg", 1)

#Maximum size of the output file
maxsize = 100

def getSize(filename):
    st = os.stat(filename)
    return st.st_size
width = min(int(img.shape[0] / 6), int(img.shape[1] / 6))
hight = max(int(img.shape[0] / 6), int(img.shape[1] / 6))

resize = cv2.resize(img, (width, (hight)))
img_ctr = resize.copy()

screen_res = 1280, 720
scale_width = screen_res[0] / min(img.shape[1], img.shape[0])
scale_hight = screen_res[1] / max(img.shape[1], img.shape[0])
scale = min(scale_width, scale_hight)

output_width = min(int(img.shape[1] * scale), int(img.shape[0] * scale))
output_hight = max(int(img.shape[1] * scale), int(img.shape[0] * scale))


# cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
# cv2.resizeWindow('Output', output_width, output_hight)

def empty(a):
    pass


# cv2.namedWindow("screen")
# cv2.createTrackbar("v1","screen",1,200,empty)
# cv2.createTrackbar("v2","screen",1,200,empty)
kernal = np.ones((5, 5))


def process(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 1)
    # v1 = cv2.getTrackbarPos("v1","screen")
    # v2 = cv2.getTrackbarPos("v2","screen")
    canny = cv2.Canny(blur, 50, 50)
    dilate = cv2.dilate(canny, kernal, iterations=2)
    erode = cv2.erode(dilate, kernal, iterations=1)

    return canny, erode, gray


def getcontour(img):
    large = np.array([])
    maxArea = 0
    contour, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    for ctr in contour:
        area = cv2.contourArea(ctr)
        if area > 14000:
            cv2.drawContours(img_ctr, ctr, -1, (55, 255, 55), 3)
            peri = cv2.arcLength(ctr, True)
            approx = cv2.approxPolyDP(ctr, 0.02 * peri, True)
            if len(approx) == 4 and area > maxArea:
                large = approx
                maxArea = area
    cv2.drawContours(img_ctr, large, -1, (55, 0, 255), 15)
    return large


def reorder(points):
    points = points.reshape((4, 2))
    new_points = np.zeros((4, 1, 2), np.int32)
    add = np.sum(points, axis=1)
    # print('add = ',add)
    new_points[0] = points[np.argmin(add)]
    new_points[3] = points[np.argmax(add)]

    sub = np.diff(points, axis=1)
    new_points[1] = points[np.argmin(sub)]
    new_points[2] = points[np.argmax(sub)]
    # print('rearranged points =',new_points)

    return new_points


def cvtBlack(img):
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # # v1 = cv2.getTrackbarPos("v1","screen")
    # (thres, black) = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    #cv2.imshow("lab", lab)

    # -----Splitting the LAB image to different channels-------------------------
    l, a, b = cv2.split(lab)
    #cv2.imshow('l_channel', l)
    #cv2.imshow('a_channel', a)
    #cv2.imshow('b_channel', b)

    # -----Applying CLAHE to L-channel-------------------------------------------
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    #cv2.imshow('CLAHE output', cl)

    # -----Merge the CLAHE enhanced L-channel with the a and b channel-----------
    limg = cv2.merge((cl, a, b))
   # cv2.imshow('limg', limg)

    # -----Converting image from LAB Color model to RGB model--------------------
    final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    # cv2.imshow('final', final)

    return final


def crop(img, large):
    # print(large.shape)
    large = reorder(large)
    pt1 = np.float32(large)
    pt2 = np.float32([[0, 0], [width, 0], [0, hight], [width, hight]])
    matrix = cv2.getPerspectiveTransform(pt1, pt2)
    output = cv2.warpPerspective(img, matrix, (width, hight))
    cropped = output[10:output.shape[0]+30, 10:output.shape[1]+30]

    black = cvtBlack(cropped)

    return black, cropped


canny, erode, gray = process(resize)
large = getcontour(erode)
img_crop, black = crop(resize, large)
# cv2.imshow("img", resize)
# # cv2.imshow("gray", gray)
# cv2.imshow("canny", canny)
# cv2.imshow("erode", erode)
# cv2.imshow("img_ctr", img_ctr)
#cv2.imshow('Output', img_crop)
# cv2.imshow('cropped', black)
cv2.imwrite('final.jpg', black)
flag = 0

if flag == 0:
    if int(getSize('final.jpg'))/1000 > maxsize:
        img = Image.open('final.jpg')
        img = img.resize((width-1, hight-1), PIL.Image.ANTIALIAS)
        img.save('finall.jpg')
        flag = 1
i,j = '',''
image = PIL.Image.open('img6.jpg')
wd, ht = image.size
print(wd, ht)
if flag == 1:
    while int(getSize(str(i) + 'finall.jpg'))/1000 > maxsize:
        i = 0
        ht -= 9
        wd -= 10
        img = Image.open('finall.jpg')
        img = img.resize((wd , ht), PIL.Image.ANTIALIAS)
        # os.remove('finall.jpg')
        print(wd, ht)
        img.save(str(i) + 'finall.jpg')
if flag == 1:
    os.remove('final.jpg')


    # key = cv2.waitKey(1)
    # if key == ord('q'):
    #     break
    # elif key == ord('s'):
    #     cv2.imwrite('trial' + 'converted.jpg', black)
    #     print('saved!!!!')
    #     break

cv2.destroyAllWindows()
