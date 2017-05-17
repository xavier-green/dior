//
//  Favourites.swift
//  SwiftExample
//
//  Created by xavier green on 27/04/2017.
//  Copyright © 2017 MacMeDan. All rights reserved.
//

import Foundation
import JSQMessagesViewController

class Favourites {
    
    var writePath: URL
    var exceptionalPath: URL
    var favouritesPath: URL
    var historyBotPath: URL
    var historyUserPath: URL
    var detailsPath: URL
    
    init() {
        let documents = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true)[0]
        writePath = NSURL(fileURLWithPath: documents).appendingPathComponent("file.plist")!
        exceptionalPath = NSURL(fileURLWithPath: documents).appendingPathComponent("transac.plist")!
        favouritesPath = NSURL(fileURLWithPath: documents).appendingPathComponent("fav.plist")!
        historyBotPath = NSURL(fileURLWithPath: documents).appendingPathComponent("history_bot.plist")!
        historyUserPath = NSURL(fileURLWithPath: documents).appendingPathComponent("history_user.plist")!
        detailsPath = NSURL(fileURLWithPath: documents).appendingPathComponent("details")!
    }
    
    func read_file() -> [String] {
        print("Reading favourites list")
        let questions = NSArray(contentsOf: writePath)
        print(questions ?? "No questions")
        if (questions == nil || questions?.count == 0) {
            return []
        }
        return questions as! [String]
    }
    
    func write_to_file(questions: [String]) {
        let all_questions = questions as NSArray
        all_questions.write(toFile: writePath.path, atomically: true)
    }
    
    func read_details() -> [String] {
        print("Reading details")
        let details = NSArray(contentsOf: detailsPath)
        print(details ?? "No questions")
        if (details == nil || details?.count == 0) {
            return ["Pas d'informations pour ce message"]
        }
        return details as! [String]
    }
    
    func write_details(details: [String]) {
        let all_details = details as NSArray
        all_details.write(toFile: detailsPath.path, atomically: true)
    }
    
    func read_history() -> [Any] {
        print("Reading history of messages")
        var history_messages = [JSQMessage]()
        var bot_history = NSArray(contentsOf: historyBotPath)
        if (bot_history == nil || bot_history?.count == 0) {
            bot_history = []
        }
        var user_history = NSArray(contentsOf: historyUserPath)
        if (user_history == nil || user_history?.count == 0) {
            user_history = []
        }
        for index in 0...bot_history!.count {
            if ((user_history?.count)! == (bot_history?.count)!) {
                if ((user_history?.count)! > index) {
                    history_messages.append(JSQMessage(senderId: "Question", displayName: "Question", text: user_history?[index] as! String))
                }
                if ((bot_history?.count)! > index) {
                    history_messages.append(JSQMessage(senderId: "Bot", displayName: "Bot", text: bot_history?[index] as! String))
                }
            } else {
                if ((bot_history?.count)! > index) {
                    history_messages.append(JSQMessage(senderId: "Bot", displayName: "Bot", text: bot_history?[index] as! String))
                }
                if ((user_history?.count)! > index) {
                    history_messages.append(JSQMessage(senderId: "Question", displayName: "Question", text: user_history?[index] as! String))
                }
            }
        }
        if (history_messages.count == 0) {
            return [[JSQMessage(senderId: "Bot", displayName: "Bot", text: "Bienvenue sur DiorBot, pose moi une question ! 😀")],1]
        }
        return [history_messages,(bot_history?.count)!]
    }
    
    func write_history(questions: [JSQMessage]) {
        var bot_history = [String]()
        var user_history = [String]()
        for question in questions {
            if (question.senderId == "Bot") {
                bot_history.append(question.text)
            } else {
                user_history.append(question.text)
            }
        }
        print("Got write request for message history")
        let bot_questions = bot_history as NSArray
        bot_questions.write(toFile: historyBotPath.path, atomically: true)
        let user_questions = user_history as NSArray
        user_questions.write(toFile: historyUserPath.path, atomically: true)
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
    
    func read_file_favourites() -> Bool {
        print("Reading favourites settings")
        do {
            let favourites_bool = try String(contentsOf: favouritesPath)
            print(favourites_bool)
            if favourites_bool == "true" {
                return true
            }
            return false
        } catch {
            return false
        }
    }
    
    func write_to_favourites(favourites_bool: String) {
        do {
            try favourites_bool.write(to: favouritesPath, atomically: true, encoding: String.Encoding.utf8)
        } catch {
            print("COuldnt write favourites settings to file...")
        }
    }
    
}
