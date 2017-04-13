from treetagger import TreeTagger
tt = TreeTagger(language='french')
print(tt.tag('quelles sont les meilleures boutiques en ventes de JAdior (sacs et shoes)'))
