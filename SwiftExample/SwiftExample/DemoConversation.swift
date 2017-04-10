//
//  DemoConversation.swift
//  SwiftExample
//
//  Created by Dan Leonard on 5/11/16.
//  Copyright © 2016 MacMeDan. All rights reserved.
//

import JSQMessagesViewController

var conversation = [JSQMessage]()

let photoItem = JSQPhotoMediaItem(image: UIImage(named: "Image-1"))
let message = JSQMessage(senderId: "Bot", displayName: "Bot", text: "Bienvenue sur DiorBot, pose moi une question ! 😀")

func makeNormalConversation() -> [JSQMessage] {
    conversation = [message]
    return conversation
}
