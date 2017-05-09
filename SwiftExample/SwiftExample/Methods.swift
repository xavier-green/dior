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

    func parse_message(sentence: String, seuil: String) -> [String] {
        print("parsed msg backend")
        let parsed_msg = Server().parseMessage(sentence: sentence, seuil: seuil)
        print("Server parse message: "+parsed_msg)
        let json_parsed_msg = parse_json(json_string: parsed_msg)
        return json_parsed_msg
    }
    
    func parse_json(json_string: String) -> [String] {
        var string_response = ""
        var details = ""
        do {
            if let data = json_string.data(using: String.Encoding.utf8) {
                let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
                string_response = (json?["answer"] as? String)!
                print("interm resp: "+string_response)
                for detail in (json?["details"] as? [[String: Any]])! {
                    print(detail)
                    let item = detail["item"] as? String
                    let count = detail["count"] as? String
                    details += item!+" ("+count!+")\n"
                }
            }
        } catch {
            print("Error deserializing JSON: \(error)")
        }
        print("Answer: "+string_response)
        print("Details: "+details)
        return [string_response,details]
    }
    
}
