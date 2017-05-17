//
//  ChatViewController.swift
//  SwiftExample
//
//  Created by Dan Leonard on 5/11/16.
//  Copyright © 2016 MacMeDan. All rights reserved.
//

import UIKit
import JSQMessagesViewController

class ChatViewController: JSQMessagesViewController, UIGestureRecognizerDelegate {
    var messages = [JSQMessage]()
    
    var favourites = Favourites()
    var chat_details = [String]()
    
    var incomingBubble: JSQMessagesBubbleImage!
    var outgoingBubble: JSQMessagesBubbleImage!
    fileprivate var displayName: String!
    
    var can_send_msg = true
    
    func tapped() {
        print("Main logo tapped")
        messages = [JSQMessage]()
        favourites.write_history(questions: self.messages)
        chat_details = [String]()
        favourites.write_details(details: chat_details)
        self.collectionView?.reloadData()
    }
    
    override func viewDidLoad() {
        print("Main chat loading...")
        super.viewDidLoad()
        
        NotificationCenter.default.addObserver(self, selector: #selector(self.slow_response), name: NSNotification.Name(rawValue: "TIME_OUT_BACK"), object: nil)
        
        // Setup navigation
        setupFavButton()
        
//        self.navigationItem.title = "Dior"
        navigationController?.navigationBar.barTintColor = UIColor(colorLiteralRed: 140/255, green: 140/255, blue: 140/255, alpha: 1)
        navigationController?.navigationBar.tintColor = UIColor.white
//        navigationController?.navigationBar.titleTextAttributes = [NSForegroundColorAttributeName: UIColor.white, NSFontAttributeName: UIFont(name: "Baskerville", size: 40)!]
        
        let titleView = UILabel()
        titleView.text = "Dior"
        titleView.font = UIFont(name: "Baskerville", size: 40)!
        titleView.textColor = UIColor.white
        titleView.frame  = CGRect(x: 0, y: 0, width: 100, height: 30)
        self.navigationItem.titleView = titleView
        
        let recognizer = UITapGestureRecognizer(target: self, action: #selector(self.tapped))
        titleView.isUserInteractionEnabled = true
        titleView.addGestureRecognizer(recognizer)
        
//        self.navigationController?.navigationBar.setTitleVerticalPositionAdjustment(5, for: .default)
        
        incomingBubble = JSQMessagesBubbleImageFactory().incomingMessagesBubbleImage(with: UIColor.jsq_messageBubbleGreen())
        outgoingBubble = JSQMessagesBubbleImageFactory().outgoingMessagesBubbleImage(with: UIColor.jsq_messageBubbleBlue())
        
        collectionView?.collectionViewLayout.incomingAvatarViewSize = .zero
        collectionView?.collectionViewLayout.outgoingAvatarViewSize = .zero
        
        // This is a beta feature that mostly works but to make things more stable it is diabled.
        collectionView?.collectionViewLayout.springinessEnabled = false
        
        automaticallyScrollsToMostRecentMessage = true

        self.collectionView?.reloadData()
        self.collectionView?.layoutIfNeeded()
        
        let button: UIButton = UIButton(type: .custom)
        button.setImage(UIImage(named: "settings"), for: UIControlState.normal)
        button.addTarget(self, action: #selector(self.addTapped), for: UIControlEvents.touchUpInside)
        button.frame = CGRect(x: 0, y: 0, width: 30, height: 30)
        let barButton = UIBarButtonItem(customView: button)
        navigationItem.leftBarButtonItem = barButton
        
        let diorbot: UIButton = UIButton(type: .custom)
        diorbot.setTitle("DiorBot", for: UIControlState.normal)
        diorbot.frame = CGRect(x: 0, y: 0, width: 80, height: 30)
        diorbot.titleLabel?.font = UIFont(name: "Baskerville", size: 20)!
        let barbotButton = UIBarButtonItem(customView: diorbot)
        navigationItem.rightBarButtonItem = barbotButton
        
    }
    
    override var preferredStatusBarStyle: UIStatusBarStyle {
        return .lightContent
    }
    
    @objc func addTapped() {
        print("tapped")
        let storyboard = UIStoryboard(name: "Settings", bundle: nil)
        let controller = storyboard.instantiateViewController(withIdentifier: "SettingsControl") as! UINavigationController
        self.present(controller, animated: true, completion: nil)
    }
    
    func setupFavButton() {
        let button = UIButton.init(type: .custom)
        button.setImage(UIImage.init(named: "star"), for: UIControlState.normal)
        button.frame = CGRect.init(x: 0, y: 0, width: 30, height: 20)
        self.inputToolbar.contentView?.leftBarButtonItem = button
    }
    
    func favTapped() {
//        self.present(UINavigationController(rootViewController: SettingsTableViewController()), animated: true, completion: nil)
        self.send_message(text: "Question favorite", senderId: "Question", senderDisplayName: "Question", date: Date())
    }
    
    func fake_reply(message: JSQMessage) {
        
        self.messages.append(message)
        self.finishSendingMessage(animated: true)
        
    }
    
    func reply(sentence: String) {
        
        let message_reply = JSQMessage(senderId: "Bot", senderDisplayName: "Bot", date: Date(), text: sentence)
        self.fake_reply(message: message_reply)
        print("writing history to file")
        favourites.write_history(questions: self.messages)
        favourites.write_details(details: self.chat_details)
        self.can_send_msg = true
        
    }
    
    func toogleTyping() {
        
        self.showTypingIndicator = !self.showTypingIndicator
        
    }
    
    func send_message(sentence: String){
        print("sending {"+sentence+"} to server")
        if self.can_send_msg {
            
            self.can_send_msg = false
            let seuil: String = favourites.read_file_transac()
            DispatchQueue.global(qos: .background).async {
                let parsed_messages = Methods().parse_message(sentence: sentence, seuil: seuil)
                DispatchQueue.main.async {
                    print("done")
                    self.chat_details.append(parsed_messages[1])
                    self.toogleTyping()
                    self.reply(sentence: parsed_messages[0])
                }
            }
            
        } else {
            let alert = UIAlertController(title: "Attention", message: "Veuillez attendre la réponse du bot avant d'envoyer un nouveau message", preferredStyle: UIAlertControllerStyle.alert)
            alert.addAction(UIAlertAction(title: "Fermer", style: UIAlertActionStyle.cancel, handler: nil))
            self.present(alert, animated: true, completion: nil)
        }
    }
    
    // MARK: JSQMessagesViewController method overrides
    override func didPressSend(_ button: UIButton, withMessageText text: String, senderId: String, senderDisplayName: String, date: Date) {
        /**
         *  Sending a message. Your implementation of this method should do *at least* the following:
         *
         *  1. Play sound (optional)
         *  2. Add new id<JSQMessageData> object to your data source
         *  3. Call `finishSendingMessage`
         */
        
        self.send_message(text: text, senderId: senderId, senderDisplayName: senderDisplayName, date: date)
        
    }
    
    func send_message(text: String, senderId: String, senderDisplayName: String, date: Date) {
        print("got message: "+text)
        let message = JSQMessage(senderId: senderId, senderDisplayName: senderDisplayName, date: date, text: text)
//        let message_reply = JSQMessage(senderId: "Bot", senderDisplayName: "Bot", date: date, text: text)
        self.messages.append(message)
        print("done appending message")
        self.finishSendingMessage(animated: true)
        print("added to screen")
        
        toogleTyping()
        print("sending msg to server")
        self.send_message(sentence: text)
//        DispatchQueue.main.asyncAfter(deadline: .now() + 5.0, execute: {
//            self.fake_reply(message: message_reply)
//        })
    }
    
    override func didPressAccessoryButton(_ sender: UIButton) {
        self.inputToolbar.contentView!.textView!.resignFirstResponder()
        
        let favorits: [String] = favourites.read_file()
        
        let sheet = UIAlertController(title: "Vos questions favorites", message: nil, preferredStyle: .actionSheet)
        
        for question in favorits {
            sheet.addAction(UIAlertAction(title: question, style: .default) { (action) in
                self.writeQuestionToInput(question: question)
//                self.send_message(text: question, senderId: self.senderId(), senderDisplayName: self.senderId(), date: Date())
            })
        }
        
        let cancelAction = UIAlertAction(title: "Annuler", style: .cancel, handler: nil)
        sheet.addAction(cancelAction)
        
        self.present(sheet, animated: true, completion: nil)
    }
    
    func buildLocationItem() -> JSQLocationMediaItem {
        let ferryBuildingInSF = CLLocation(latitude: 37.795313, longitude: -122.393757)
        
        let locationItem = JSQLocationMediaItem()
        locationItem.setLocation(ferryBuildingInSF) {
            self.collectionView!.reloadData()
        }
        
        return locationItem
    }
    
    func addMedia(_ media:JSQMediaItem) {
        let message = JSQMessage(senderId: self.senderId(), displayName: self.senderDisplayName(), media: media)
        self.messages.append(message)
        
        //Optional: play sent sound
        
        self.finishSendingMessage(animated: true)
    }
    
    
    //MARK: JSQMessages CollectionView DataSource
    
    override func senderId() -> String {
        return "Question"
    }
    
    override func senderDisplayName() -> String {
        return "Question"
    }
    
    override func collectionView(_ collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
        return messages.count
    }
    
    override func collectionView(_ collectionView: JSQMessagesCollectionView, messageDataForItemAt indexPath: IndexPath) -> JSQMessageData {
        return messages[indexPath.item]
    }
    
    override func collectionView(_ collectionView: JSQMessagesCollectionView, messageBubbleImageDataForItemAt indexPath: IndexPath) -> JSQMessageBubbleImageDataSource {
        
        return messages[indexPath.item].senderId == self.senderId() ? outgoingBubble : incomingBubble
    }
    
    override func collectionView(_ collectionView: JSQMessagesCollectionView, attributedTextForCellTopLabelAt indexPath: IndexPath) -> NSAttributedString? {
        /**
         *  This logic should be consistent with what you return from `heightForCellTopLabelAtIndexPath:`
         *  The other label text delegate methods should follow a similar pattern.
         *
         *  Show a timestamp for every 3rd message
         */
//        if (indexPath.item % 3 == 0) {
//            let message = self.messages[indexPath.item]
//            
//            return JSQMessagesTimestampFormatter.shared().attributedTimestamp(for: message.date)
//        }
        
        return nil
    }
    
    override func collectionView(_ collectionView: JSQMessagesCollectionView, attributedTextForMessageBubbleTopLabelAt indexPath: IndexPath) -> NSAttributedString? {
        let message = messages[indexPath.item]
        
        // Displaying names above messages
        //Mark: Removing Sender Display Name
        /**
         *  Example on showing or removing senderDisplayName based on user settings.
         *  This logic should be consistent with what you return from `heightForCellTopLabelAtIndexPath:`
         */
//        if defaults.bool(forKey: Setting.removeSenderDisplayName.rawValue) {
//            return nil
//        }
        
        let date_string = " ("+getDate(date: message.date)+")"
        
        if message.senderId == self.senderId() {
            return NSAttributedString(string: "Vous"+date_string)
        }

        return NSAttributedString(string: message.senderDisplayName+date_string)
    }
    
    override func collectionView(_ collectionView: JSQMessagesCollectionView, layout collectionViewLayout: JSQMessagesCollectionViewFlowLayout, heightForCellTopLabelAt indexPath: IndexPath) -> CGFloat {
        /**
         *  Each label in a cell has a `height` delegate method that corresponds to its text dataSource method
         */
        
        /**
         *  This logic should be consistent with what you return from `attributedTextForCellTopLabelAtIndexPath:`
         *  The other label height delegate methods should follow similarly
         *
         *  Show a timestamp for every 3rd message
         */
//        if indexPath.item % 3 == 0 {
//            return kJSQMessagesCollectionViewCellLabelHeightDefault
//        }
    
        return 0.0
    }

    override func collectionView(_ collectionView: JSQMessagesCollectionView, layout collectionViewLayout: JSQMessagesCollectionViewFlowLayout, heightForMessageBubbleTopLabelAt indexPath: IndexPath) -> CGFloat {
        
        /**
         *  Example on showing or removing senderDisplayName based on user settings.
         *  This logic should be consistent with what you return from `attributedTextForCellTopLabelAtIndexPath:`
         */
//        if defaults.bool(forKey: Setting.removeSenderDisplayName.rawValue) {
//            return 0.0
//        }
        
        /**
         *  iOS7-style sender name labels
         */
        let currentMessage = self.messages[indexPath.item]
        
        if currentMessage.senderId == self.senderId() {
            return 0.0
        }
        
        if indexPath.item - 1 > 0 {
            let previousMessage = self.messages[indexPath.item - 1]
            if previousMessage.senderId == currentMessage.senderId {
                return 0.0
            }
        }
        
        return kJSQMessagesCollectionViewCellLabelHeightDefault;
    }
    
    override func collectionView(_ collectionView: UICollectionView, didHighlightItemAt indexPath: IndexPath) {
        let currentMessage = self.messages[indexPath.item]
        print("Selected: "+currentMessage.text)
    }
    override func collectionView(_ collectionView: UICollectionView, didSelectItemAt indexPath: IndexPath) {
        let currentMessage = self.messages[indexPath.item]
        print("Selected: "+currentMessage.text)
    }
    override func collectionView(_ collectionView: JSQMessagesCollectionView, didTapMessageBubbleAt indexPath: IndexPath) {
        let message = self.messages[indexPath.item]
        if (message.senderDisplayName == "Question") {
            if favourites.read_file_favourites() {
                self.add_to_fav_popup(question: message.text)
            } else {
                self.writeQuestionToInput(question: message.text)
            }
        } else {
            self.see_info(index: indexPath.row)
        }
    }
    
    func add_to_fav_popup(question: String) {
        let alert = UIAlertController(title: "Ajouter aux favoris", message: "Voulez vous ajouter la question {"+question+"} à vos favoris ?", preferredStyle: UIAlertControllerStyle.alert)
        alert.addAction(UIAlertAction(title: "Oui", style: UIAlertActionStyle.default, handler: {
            action in self.add_to_fav(question: question)
        }))
        alert.addAction(UIAlertAction(title: "Non", style: UIAlertActionStyle.cancel, handler: nil))
        self.present(alert, animated: true, completion: nil)
    }
    
    func see_info(index: Int) {
        print(self.chat_details)
        let details_index = quotient(a: index, b: 2)
        let alert = UIAlertController(title: "Informations", message: "Voici d'où les infos sont extraites:\n"+self.chat_details[details_index], preferredStyle: UIAlertControllerStyle.alert)
        alert.addAction(UIAlertAction(title: "Fermer", style: UIAlertActionStyle.cancel, handler: nil))
        self.present(alert, animated: true, completion: nil)
    }
    
    func add_to_fav(question: String) {
        let favorits: [String] = favourites.read_file()
        if !favorits.contains(question) {
            let all_questions = favorits+[question]
            favourites.write_to_file(questions: all_questions)
        }
    }

    func slow_response() {
        DispatchQueue.main.async {
            self.toogleTyping()
            self.chat_details.append("Aucune info pour les erreurs")
            self.reply(sentence: "Malheureusement le server a mis trop longtemps à répondre...")
        }
    }
    
    func getDate(date: Date) -> String {
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "dd/MM/yyyy HH:mm"
        return dateFormatter.string(from: date)
    }

    func quotient(a: Int, b: Int) -> Int {
        return ~(~(a/b))
    }
    
    func writeQuestionToInput(question: String) {
        self.inputToolbar.contentView!.textView!.becomeFirstResponder()
        self.inputToolbar.contentView?.textView?.text = question+" "
        self.inputToolbar.contentView?.rightBarButtonItem?.isEnabled = true
    }
    
}
