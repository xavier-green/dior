//
//  Favourites.swift
//  SwiftExample
//
//  Created by xavier green on 27/04/2017.
//  Copyright © 2017 MacMeDan. All rights reserved.
//

import Foundation

class Favourites {
    
    var writePath: URL
    var exceptionalPath: URL
    
    init() {
        let documents = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true)[0]
        writePath = NSURL(fileURLWithPath: documents).appendingPathComponent("file.plist")!
        exceptionalPath = NSURL(fileURLWithPath: documents).appendingPathComponent("transac.plist")!
    }
    
    func read_file() -> [String] {
        print("Reading favourites list")
        let questions = NSArray(contentsOf: writePath) as! [String]
        print(questions)
        return questions
    }
    
    func write_to_file(questions: [String]) {
        let all_questions = questions as NSArray
        all_questions.write(toFile: writePath.path, atomically: true)
    }
    
    func read_file_transac() -> String {
        print("Reading max transaction level amount")
        do {
            let transaction_level = try String(contentsOf: exceptionalPath)
            print(transaction_level)
            return transaction_level
        } catch {
            return "50000"
        }
    }
    
    func write_to_file_transac(transaction_level: String) {
        do {
            try transaction_level.write(to: exceptionalPath, atomically: true, encoding: String.Encoding.utf8)
        } catch {
            print("COuldnt write transaction level to file...")
        }
    }
    
}
