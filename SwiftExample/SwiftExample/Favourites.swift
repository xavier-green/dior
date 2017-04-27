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
    
    init() {
        let documents = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true)[0]
        writePath = NSURL(fileURLWithPath: documents).appendingPathComponent("file.plist")!
//        let writePath = documents.stringByAppendingPathComponent("file.plist")
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
    
}
