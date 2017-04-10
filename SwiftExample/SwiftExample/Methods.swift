//
//  Methods.swift
//  SwiftExample
//
//  Created by xavier green on 10/04/2017.
//  Copyright © 2017 MacMeDan. All rights reserved.
//

import Foundation
import UIKit

class Methods {
    
    // Parse Json when it starts with []
    func parseJsonArray(jsonString: String) -> [AnyObject]  {
        let data: Data = jsonString.data(using: String.Encoding.utf8, allowLossyConversion: false)!
        let json = try? JSONSerialization.jsonObject(with: data, options: [])
        let array = json as! [AnyObject]
        return array
    }
    
    // Parse Json when it starts with {}
    func parseJson(jsonString: String) -> [String:Any]  {
        let data: Data = jsonString.data(using: String.Encoding.utf8, allowLossyConversion: false)!
        let json = try? JSONSerialization.jsonObject(with: data, options: [])
        let dictionary = json as! [String:Any]
        return dictionary
    }

    func parse_message(sentence: String) -> String {
        print("parsed msg backend")
        let parsed_msg = Server().parseMessage(sentence: sentence.addingPercentEncoding(withAllowedCharacters: .urlHostAllowed)!)
        print("Server parse message: "+parsed_msg)
        return parsed_msg
    }
    
}
