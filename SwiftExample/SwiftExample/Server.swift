//
//  Server.swift
//  SwiftExample
//
//  Created by xavier green on 10/04/2017.
//  Copyright © 2017 MacMeDan. All rights reserved.
//

import Foundation
import UIKit

class Server {
    
    private let BASE_URL: String = Config.serverURL
    private let SERVER_USERNAME: String = Config.serverUsername
    private let SERVER_PASSWORD: String = Config.serverPassword
    
    private var resultData: String = ""
    
    //MARK: Request Functions
    
    func connectToServer(url: String, params: [[String]], method: String, notificationString: String) -> String {
        
        if method=="GET" {
            
            let connectionUrl = constructURL(base: BASE_URL, url: url, params: params)
            return getRequest(connectionUrl: connectionUrl, notificationString: notificationString)
            
        } else if method=="POST" {
            
            return postRequest(connectionUrl: BASE_URL+url, params: params, notificationString: notificationString)
            
        } else if method=="PUT" {
            
            let connectionUrl = constructURL(base: BASE_URL, url: url, params: params)
            return putRequest(connectionUrl: connectionUrl, notificationString: notificationString)
            
        }
        
        return ""
        
    }
    
    func putRequest(connectionUrl: String, notificationString: String) -> String {
        
        print("Connecting to ",connectionUrl)
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest=TimeInterval(20)
        config.timeoutIntervalForResource=TimeInterval(60)
        let authString = constructHeaders()
        config.httpAdditionalHeaders = ["Authorization" : authString]
        let session = URLSession(configuration: config)
        let url = URL(string: connectionUrl)!
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        
        return sendRequest(session: session, request: request, notificationString: notificationString)
        
    }
    
    func getRequest(connectionUrl: String, notificationString: String) -> String {
        
        print("Connecting to ",connectionUrl)
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest=TimeInterval(20)
        config.timeoutIntervalForResource=TimeInterval(60)
        let authString = constructHeaders()
        config.httpAdditionalHeaders = ["Authorization" : authString]
        let session = URLSession(configuration: config)
        let url = URL(string: connectionUrl)!
        let request = URLRequest(url: url)
        
        return sendRequest(session: session, request: request, notificationString: notificationString)
        
    }
    
    func postRequest(connectionUrl: String, params: [[String]], notificationString: String) -> String {
        
        print("Connecting to ",connectionUrl)
        
        let postParams = constructParams(params: params)
        let sendData = postParams.data(using: String.Encoding.utf8)!
        
        //print(postParams)
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest=TimeInterval(20)
        config.timeoutIntervalForResource=TimeInterval(60)
        let authString = constructHeaders()
        config.httpAdditionalHeaders = ["Authorization" : authString]
        let session = URLSession(configuration: config)
        let url = URL(string: connectionUrl)!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        request.httpBody = sendData
        
        return sendRequest(session: session, request: request, notificationString: notificationString)
        
    }
    
    func sendRequest(session: URLSession, request: URLRequest, notificationString: String) -> String {
        
        print("sending request")
        
        let semaphore = DispatchSemaphore(value: 0)
        var dataString: String?
        var errors: String?
        
        session.dataTask(with: request, completionHandler: { (data, response, error) in
            if error != nil {
                NotificationCenter.default.post(name: Notification.Name(rawValue: "TIME_OUT_BACK"), object: errors)
                return
            }
            if let httpStatus = response as? HTTPURLResponse, httpStatus.statusCode != 200 {
                print("statusCode should be 200, but is \(httpStatus.statusCode)")
                //print("response = \(response)")
                print("******** REQUEST ERROR")
                errors = NSString(data: data!, encoding: String.Encoding.utf8.rawValue) as? String
                
                // In case of error, send notification observed from App Delegate
                // Shows pop up the says an error happened
                NotificationCenter.default.post(name: Notification.Name(rawValue: "ERROR_BACK"), object: errors)
                return
                
            }
            dataString = NSString(data: data!, encoding: String.Encoding.utf8.rawValue) as? String
            //print(dataString)
            
            semaphore.signal()
            
            print("Done, sending notification: ",notificationString)
            
            //            NotificationCenter.default.post(name: Notification.Name(rawValue: notificationString), object: dataString)
            
        }).resume()
        
        _ = semaphore.wait(timeout: .distantFuture)
        
        if let error = errors {
            print(error)
        }
        
        return dataString!
        
    }
    
    //MARK: Set Headers for request
    
    func constructHeaders() -> String {
        
        let loginString = String(format: "%@:%@", SERVER_USERNAME, SERVER_PASSWORD)
        let loginData = loginString.data(using: String.Encoding.utf8)!
        let base64LoginString = loginData.base64EncodedString()
        let authString = "Basic \(base64LoginString)"
        //print("authstring: ",authString)
        return authString
        
    }
    
    func constructURL(base: String, url: String, params: [[String]]) -> String {
        if params[0]==[] {
            let finalUrl = base + url
            return finalUrl
        } else {
            var finalUrl = base + url + "?"
            for param in params {
                finalUrl += param[0]+"="+param[1]+"&"
            }
            return finalUrl
        }
    }
    
    //MARK: Set Parameters for request
    
    func constructParams(params: [[String]]) -> String {
        
        var finalUrl = ""
        print("params length: ",params.count)
        if (params.count > 0) {
            for param in params {
                //print("param: ",param)
                finalUrl += param[0]+"="+param[1]+"&"
            }
        }
        return finalUrl
        
    }
    
    func parseMessage(sentence: String) -> String {
        print("Getting user attribute")
        
        let url: String = "/"+sentence
        let params: [[String]] = [[]]
        
        return connectToServer(url: url, params: params, method: "GET", notificationString: "PARSED_MSG")
    }
    
    
}
