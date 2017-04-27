//
//  FavouritesViewController.swift
//  SwiftExample
//
//  Created by xavier green on 27/04/2017.
//  Copyright © 2017 MacMeDan. All rights reserved.
//

import UIKit

class FavouritesViewController: UIViewController, UITableViewDelegate,UITableViewDataSource {
    
    var all_questions = [String]()
    var favourites = Favourites()
    
    @IBAction func retour(_ sender: Any) {
        dismiss(animated: true, completion: nil)
    }
    
    @IBOutlet var favourite_questions_view: UITableView!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        favourite_questions_view.delegate=self
        favourite_questions_view.dataSource=self
        all_questions = favourites.read_file()
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    func numberOfSections(in tableView: UITableView) -> Int {
        // #warning Incomplete implementation, return the number of sections
        return 1
    }
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return self.all_questions.count
    }
    internal func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let row = indexPath.row
        let cell = tableView.dequeueReusableCell(withIdentifier: "qCell",
                                                 for: indexPath) as! questionCell
        cell.question.text = self.all_questions[row]
        return cell
    }
    
    func tableView(_ tableView: UITableView, didHighlightRowAt indexPath: IndexPath) {
        let row = indexPath.row
        self.delete_popup(index: row)
    }
    
    func delete_popup(index: Int) {
        let alert = UIAlertController(title: "Supprimer des favoris", message: "Voulez vous supprimer la question {"+self.all_questions[index]+"} de vos favorits ?", preferredStyle: UIAlertControllerStyle.alert)
        alert.addAction(UIAlertAction(title: "Oui", style: UIAlertActionStyle.default, handler: {
            action in self.delete(index: index)
        }))
        alert.addAction(UIAlertAction(title: "Non", style: UIAlertActionStyle.cancel, handler: nil))
        self.present(alert, animated: true, completion: nil)
    }
    
    func delete(index: Int) {
        self.favourite_questions_view.beginUpdates()
        self.all_questions.remove(at: index)
        self.favourite_questions_view.deleteRows(at: [IndexPath(row: index, section: 0)], with: .automatic)
        self.favourite_questions_view.endUpdates()
        favourites.write_to_file(questions: self.all_questions)
    }

}

class questionCell: UITableViewCell {
    @IBOutlet weak var question: UILabel!
}
