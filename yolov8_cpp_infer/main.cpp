#include <iostream>

#include <vector>

#include <getopt.h>



#include <opencv2/opencv.hpp>



#include "inference.h"



using namespace std;

using namespace cv;



int main(int argc, char **argv)

{
    bool runOnGPU = true;



    //

    // Pass in either:

    //

    // "yolov8s.onnx" or "yolov5s.onnx"

    //

    // To run Inference with yolov8/yolov5 (ONNX)

    //



    // Note that in this example the classes are hard-coded and 'classes.txt' is a place holder.
    std::string onnxFilePath = "/home/itachi/Desktop/battery_code/yolov8_cpp_infer/models/battery_yolov8s.onnx"; // Set your onnx file path
    Inference inf(onnxFilePath, cv::Size(640, 640), "classes.txt", runOnGPU);


    std::string videoPath = "/home/itachi/Desktop/battery_code/video/truck_battery.avi";
    cv::VideoCapture cap(videoPath);
    if (!cap.isOpened()) {
        std::cerr << "Error: Unable to open the camera\n";
        return -1;
    }

    while (cv::waitKey(1) < 0) {
        cv::Mat frame;
        cap >> frame;
        if (frame.empty()) {
            std::cerr << "Error: Blank frame grabbed\n";
            break;
        }


        // Inference starts here...

        std::vector<Detection> output = inf.runInference(frame);



        int detections = output.size();

        std::cout << "Number of detections:" << detections << std::endl;



        for (int i = 0; i < detections; ++i)

        {

            Detection detection = output[i];



            cv::Rect box = detection.box;

            cv::Scalar color = detection.color;



            // Detection box

            cv::rectangle(frame, box, color, 20);



            // Detection box text

            std::string classString = detection.className + ' ' + std::to_string(detection.confidence).substr(0, 4);

            cv::Size textSize = cv::getTextSize(classString, cv::FONT_HERSHEY_DUPLEX, 1, 2, 0);

            cv::Rect textBox(box.x, box.y - 40, textSize.width + 10, textSize.height + 20);



            cv::rectangle(frame, textBox, color, cv::FILLED);

            cv::putText(frame, classString, cv::Point(box.x + 5, box.y - 10), cv::FONT_HERSHEY_DUPLEX, 1, cv::Scalar(0, 0, 0), 2, 0);

        }

        // Inference ends here...



        // This is only for preview purposes

        float scale = 0.2;

        cv::resize(frame, frame, cv::Size(frame.cols*scale, frame.rows*scale));

        cv::imshow("Inference", frame);

    }

}
