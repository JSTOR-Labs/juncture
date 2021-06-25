<param ve-config title="Documentation" component="default" class="documentation" fixed-header>

[<i class="fas fa-arrow-circle-left"></i> Home](/docs) <br />
[Linking Entities in a Section of Your Essay](#section-link) <br />
[Linking Entities for the Entire Essay](#whole-essay-link) <br />
[Adding Maps <i class="fas fa-arrow-circle-right"></i>](/docs/adding-maps)
___
# Linking Data Entities

While writing your visual essay, you're bound to come across a large variety of entities that your readers may want to know more about. Entities are kind of like nouns; they include persons, places, things, and general concepts. Another way to think about entities is that they are things which would have an entry in Wikipedia. 

Much of the knowledge in Wikipedia has been structured into a network of relationships called a semantic graph. The semantic graph behind Wikipedia is called Wikidata. Your essay can draw on the knowledge available in Wikidata by tagging relevant entities with an item identifier. If your readers are unfamiliar with a particular item in your essay, a description can be automaticaly generated so long as the identifier has been included in your essay's code.

# Linking Entities in a Section of Your Essay
<param id="section-link">

To link an entity in a particular section of your essay, you can use a `<param ve-entity>` tag in that section:

```html
<param ve-entity title="Black Lives Matter Movement" eid="Q19600530" aliases="#BLM">
```

The only required attribute is the `eid` number which corresponds to the [Wikidata identifier number for Black Lives Matter](https://www.wikidata.org/wiki/Q19600530). You can find the identifier for the concept you're looking for by executing a search on the Wikidata website. If the concept is not there, you can also add it yourself!

When we look at the entry for Black Lives Matter on Wikidata, we see a label (or name) for the movement in many languages and a variety of aliases (or alternative names). We can see that it is an instance of a social movement, see its logo, the names of its founders, images/videos of Black Lives Matter protests, and much more. 

The linked data in Wikidata can be pulled in to give your readers more context around a particular item. The default behavior in the Visual Essay Tool is to supply an image and a definition. When your essay is rendered, a link to this data is automatically created where the label (or an alias is used). The label is defined on the Wikidata page. Wikidata often includes aliases as well. The `alias` attribute allows you to add another even more names. This is useful if your essay uses a name that is not actually found in Wikidata.

Looking at our example `<param ve-entity>`tag, there is also a `title` attribute. This attribute is mainly for the essay writer to keep track of what the entity is. An `eid` number by itself is just a identifying number, so a human reader would not know what an entity is without the description found in the `title` attribute. There is no requirement to include a `title` attribute, but writing your essay would become confusing without this human-readable data.

Once an entity has been linked in a particular section of your essay, an informational link is automatically generated on any text that contains either a label or alias for that entity. *These links are only generated within the particular section where the entity tag was written.* In the next section, we discuss how to create links for *all mentions* in the entire essay.

In addition to using a `<param ve-entity>` tag, you can declare an entity on a set of words by using a `<span ve-entity>` tag:
```html
<span ve-entity title="Black Lives Matter Movement" eid="Q19600530">human rights activists</span>
```

In this case, a reader could click on the text <span ve-entity title="Black Lives Matter Movement" eid="Q19600530">human rights activists</span> which would create a pop-up with a description of the Black Lives Matter movement. Try clicking on the entity in the previous sentence to see the result.

# Linking Entities for the Entire Essay
<param id="whole-essay-link">

If you want to link a set of entities for your entire essay, create those links before the first section of the essay. This practice is so common that we have called "Linked Data Tags" one of the [Four Parts of a Visual Essay](https://docs.visual-essays.app/parts-of-essay/).

1. Configuration (the content of `param ve-config`)
2. Linked Data Tags (the content of `param ve-entity` tags)
3. Body (the combined sections of written and visual argument)
4. References (the references/footnotes for the argument)

If you have done programming before, you might recognize this as the difference between a "local" and "global" scope. If you haven't programmed before, the only thing to remember is that linked data entities declared at the beginning of your essay apply to the whole essay. If a linked data entity is declared in the body of your visual essay within a particular section, it will only create links for that particular section.

____
[<i class="fas fa-arrow-circle-left"></i> Home](/docs) | [Adding Maps <i class="fas fa-arrow-circle-right"></i>](/docs/adding-maps)
